#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include <errno.h>
#include <signal.h>

#ifdef __linux

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

typedef int socket_t;
static pthread_t _pid;

#define M_COLOR  "\033[32m"
#define E_COLOR  "\033[31m"
#define W_COLOR  "\033[35m"
#define I_COLOR  "\033[33m"
#define R_COLOR  "\033[0m"

#define socket_init()       ((void)0)  
#define closesocket(fd)     close(fd)
#define get_socket_error()  strerror(errno) 
#define start_thread(func)  pthread_create(&_pid, NULL, (void *(*)(void *))func, NULL)

#endif /* __linux */

#ifdef  _WIN32
#include <Windows.h>
#include <WinSock2.h>
#include <Ws2tcpip.h>

#ifdef _MSC_VER 
#pragma comment(lib, "Ws2_32.lib")
#endif

/* 不对windows通过颜色输出支持 */
#define E_COLOR  ""
#define W_COLOR  ""
#define R_COLOR  ""

typedef SOCKET socket_t;

char socket_error_buf[256];
static const char *get_socket_error(void)
{
    int err_code = WSAGetLastError();
    FormatMessage(FORMAT_MESSAGE_IGNORE_INSERTS | FORMAT_MESSAGE_FROM_SYSTEM, 
        NULL, err_code, 0, socket_error_buf, sizeof socket_error_buf, NULL);
    return socket_error_buf;
}

static bool eregec_socket_init() 
{
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData)) {
        eregec_perror("Socke Init Failed: %s", get_get_socket_error());
        return false;
    }

    return true;
} 

#define start_thread(func)  CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)func, NULL, 0, NULL)

#endif /* _WIN32 */


#include "eregec.h"

#define eregec_perror(...)    printf(M_COLOR"PlatformClient: "E_COLOR"Error: "R_COLOR __VA_ARGS__)
#define eregec_pwarning(...)  printf(M_COLOR"PlatformClient: "W_COLOR"Warning: "R_COLOR __VA_ARGS__)
#define eregec_pinfo(...)     printf(M_COLOR"PlatformClient: "I_COLOR"Info: "R_COLOR __VA_ARGS__)
#define BAD_SOCKET            (socket_t)0

#define is_connected(fd)      ((fd) && (fd) != BAD_SOCKET)

#define MAX_ID_SIZE           127
#define MAX_NAME_SIZE         127
#define MAX_HOST_SIZE         127
#define MAX_ERROR_SIZE        1023
#define MAX_SOCKET_BUF_SIZE   1023
#define MAX_DATA_COUNT        32

#define DATA_SOCKET           0
#define COMMAND_SOCKET        1
static const char *SOCKET_NAME[] = {"Data Socket", "Command Socket"};

struct {
    bool is_init;
    char name[MAX_NAME_SIZE + 1];
    char password[MAX_NAME_SIZE + 1];
    char host[MAX_HOST_SIZE + 1];
    int port;

    socket_t data_socket;
    socket_t command_socket;

    char int_data_name[MAX_DATA_COUNT][MAX_NAME_SIZE];
    int  int_data_value[MAX_DATA_COUNT];
    int  int_data_count;

    char  float_data_name[MAX_DATA_COUNT][MAX_NAME_SIZE];
    float float_data_value[MAX_DATA_COUNT];
    int   float_data_count;

    char string_data_name[MAX_DATA_COUNT][MAX_NAME_SIZE];
    char string_data_value[MAX_DATA_COUNT][MAX_NAME_SIZE];
    int  string_data_count;

    const char *(*callback_func)(const char *);
} platform_client;

/*
* head:
* 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"
* 第二行：Socket类型，取值为 "Data Socket" 或者 "Cammand Socket"
* 第三行：平台名称
* 第四行：设备ID号
* 第五行：结束标记，固定为"End"
*/
static char *create_head(char *buf, int socket_type)
{
    strcpy(buf, "Electronic Ecological Estanciero Platform Socket\n");
    strcat(buf, SOCKET_NAME[socket_type]);
    strcat(buf, "\n");
    strcat(buf, platform_client.name);
    strcat(buf, "\n");
    strcat(buf, platform_client.password);
    strcat(buf, "\nEnd");
    return buf;
}

static bool send_string(int socket_type, const char *string)
{
    socket_t *pfd;

    if (string == NULL || string[0] == 0)
        return false;

    switch (socket_type) {
        case DATA_SOCKET: pfd = &platform_client.data_socket; break;
        case COMMAND_SOCKET: pfd = &platform_client.command_socket; break;
        default: return false;
    }

    if (!is_connected(*pfd)) {
        eregec_perror("%s: send(): socket not connected(bad socket)\n", SOCKET_NAME[socket_type]);
        return false;
    }

    if (send(*pfd, string, strlen(string), 0) <= 0) {
        eregec_perror("%s: send(): %s\n", SOCKET_NAME[socket_type], get_socket_error());
        eregec_perror("%s Broken!\n",  SOCKET_NAME[socket_type]);
        *pfd = BAD_SOCKET;
        return false;
    }
    return true;
}

static bool recv_string(int socket_type, char *string)
{
    socket_t *pfd;

    switch (socket_type) {
        case DATA_SOCKET: pfd = &platform_client.data_socket; break;
        case COMMAND_SOCKET: pfd = &platform_client.command_socket; break;
        default: return false;
    }

    if (!is_connected(*pfd)) {
        eregec_perror("%s: recv(): socket not connected(bad socket)\n", SOCKET_NAME[socket_type]);
        return false;
    }

    int ret;
    if ((ret = recv(*pfd, string, MAX_SOCKET_BUF_SIZE, 0)) <= 0) {
        if (ret)
            eregec_perror("%s: recv(): %s\n",  SOCKET_NAME[socket_type], get_socket_error());
        eregec_perror("%s Broken!\n",  SOCKET_NAME[socket_type]);
        *pfd = BAD_SOCKET;
        return false;
    }
    string[ret] = 0;
    return true;
}

static socket_t connect_socket(int socket_type)
{
    socket_t fd; 
    char recv_buf[MAX_SOCKET_BUF_SIZE + 1];
    struct sockaddr_in servaddr;
    char *host = platform_client.host;
    int port = platform_client.port;

    if (!platform_client.is_init) {
        eregec_perror("cannot connect server! platform client not init!\n");
        return BAD_SOCKET;
    }

    eregec_pinfo("%s: Try to connect server %s:%d\n", SOCKET_NAME[socket_type], host, port);
    if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        eregec_perror("%s connect faild: socket(): %s\n", SOCKET_NAME[socket_type], get_socket_error());
        return BAD_SOCKET;
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &servaddr.sin_addr) <= 0) {
        eregec_perror("%s connect faild: inet_pton(): %s\n", SOCKET_NAME[socket_type], get_socket_error());
        return BAD_SOCKET;
    }
    if (connect(fd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
        eregec_perror("%s connect failed: connect(): %s\n", SOCKET_NAME[socket_type], get_socket_error());
        return BAD_SOCKET;
    }

    recv(fd, recv_buf, MAX_SOCKET_BUF_SIZE, 0);
    if (strcmp(recv_buf, "Electronic Ecological Estanciero Server")) {
        eregec_perror("%s connect failed: Bad Server Return\n", SOCKET_NAME[socket_type]);
        closesocket(fd);
        return BAD_SOCKET;
    }

    create_head(recv_buf, socket_type);
    send(fd, recv_buf, strlen(recv_buf), 0);
    memset(recv_buf, 0, sizeof recv_buf);
    recv(fd, recv_buf, MAX_SOCKET_BUF_SIZE, 0);
    if (strcmp(recv_buf, "OK")) {
        eregec_perror("%s connect failed: Server return: %s\n", SOCKET_NAME[socket_type], recv_buf);
        closesocket(fd);
        return BAD_SOCKET;
    }
    eregec_pinfo("%s is connected\n", SOCKET_NAME[socket_type]);

    return fd;
}

static void get_cmd(void)
{
    char cmd_buf[MAX_SOCKET_BUF_SIZE + 1];

    eregec_pinfo("get_cmd: start get cmd thread ...\n");
    while (is_connected(platform_client.command_socket)) {
        if (!recv_string(COMMAND_SOCKET, cmd_buf))
            continue;
        eregec_pinfo("get_cmd: client send cammand \"%s\"\n", cmd_buf);
        if (!platform_client.callback_func) {
            eregec_pwarning("get_cmd: Command Ignored(callback_func not set)\n");
            send_string(COMMAND_SOCKET, "command ignored");
            continue;
        }
        send_string(COMMAND_SOCKET, platform_client.callback_func(cmd_buf));
    }

    eregec_pinfo("get_cmd: get cmd thread stoped.\n");
}

void eregec_init(const char *name, const char *password, const char *host, int port)
{
    assert(name != NULL);
    assert(password != NULL);
    assert(host != NULL);
    assert(port > 0 && port < 65536);

    strncpy(platform_client.name, name, MAX_NAME_SIZE);
    strncpy(platform_client.password, password, MAX_NAME_SIZE);
    strncpy(platform_client.host, host, MAX_HOST_SIZE);
    platform_client.port = port;
    platform_client.is_init = true;

    if (is_connected(platform_client.data_socket)) {
        closesocket(platform_client.data_socket);
        eregec_pwarning("Data Socket was connected before init. close it.");
    }
    if (is_connected(platform_client.command_socket)) {
        closesocket(platform_client.command_socket);
        eregec_pwarning("Command Socket was connected before init. close it.");
    }

    platform_client.command_socket = BAD_SOCKET;
    platform_client.data_socket = BAD_SOCKET;

    signal(SIGPIPE, SIG_IGN);
}

bool eregec_connect(void)
{
    bool data_socket_ok = eregec_connect_data_socket();
    bool command_socket_ok = eregec_connect_command_socket();
    return data_socket_ok || command_socket_ok;
}

bool eregec_connect_command_socket(void)
{
    platform_client.command_socket = connect_socket(COMMAND_SOCKET);
    start_thread(get_cmd);
    return is_connected(platform_client.command_socket);
}

bool eregec_connect_data_socket(void)
{
    platform_client.data_socket = connect_socket(DATA_SOCKET);
    return is_connected(platform_client.data_socket);
}

void eregec_disconnect(void)
{
    eregec_disconnect_data_socket();
    eregec_disconnect_command_socket();
}

void eregec_disconnect_command_socket(void)
{
    if (is_connected(platform_client.command_socket)) {
        closesocket(platform_client.command_socket);
        platform_client.command_socket = BAD_SOCKET;
        eregec_pinfo("Command Socket: close()\n");
    }
}

void eregec_disconnect_data_socket(void)
{
    if (is_connected(platform_client.data_socket)) {
        closesocket(platform_client.data_socket);
        eregec_pinfo("Data Socket: close()\n");
        platform_client.data_socket = BAD_SOCKET;
    }
}

bool eregec_is_command_socket_connected(void)
{
    return is_connected(platform_client.command_socket);
}

bool eregec_is_data_socket_connected(void)
{
    return is_connected(platform_client.data_socket);
}

bool eregec_is_connected(void)
{
    return eregec_is_command_socket_connected() || eregec_is_data_socket_connected();
}

void eregec_set_command_callback(const char *(*callback_func)(const char *cmd))
{
    platform_client.callback_func = callback_func;
}

void eregec_set_int_data(const char *name, int value)
{
    int int_data_count = platform_client.int_data_count;
    int index = int_data_count;

    if (index >= MAX_DATA_COUNT)
        return;

    for (int i = 0; i < int_data_count; i++)
        if (!strcmp(name, platform_client.int_data_name[i])) {
            index = i;
            break;
        }

    platform_client.int_data_value[index] = value;
    if (index == int_data_count) {
        strcpy(platform_client.int_data_name[index], name);
        platform_client.int_data_count++;
    }
}

void eregec_set_float_data(const char *name, float value)
{
    int float_data_count = platform_client.float_data_count;
    int index = float_data_count;

    if (index >= MAX_DATA_COUNT)
        return;

    for (int i = 0; i < float_data_count; i++)
        if (!strcmp(name, platform_client.float_data_name[i])) {
            index = i;
            break;
        }

    platform_client.float_data_value[index] = value;
    if (index == float_data_count) {
        strcpy(platform_client.float_data_name[index], name);
        platform_client.float_data_count++;
    }
}

void eregec_set_string_data(const char *name, const char  *value)
{
    int string_data_count = platform_client.string_data_count;
    int index = string_data_count;

    if (index >= MAX_DATA_COUNT)
        return;

    for (int i = 0; i < string_data_count; i++)
        if (!strcmp(name, platform_client.string_data_name[i])) {
            index = i;
            break;
        }

    strncpy(platform_client.string_data_value[index], value, MAX_NAME_SIZE);
    if (index == string_data_count) {
        strcpy(platform_client.string_data_name[index], name);
        platform_client.string_data_count++;
    }
}

bool eregec_upload_data(void)
{
    char recv_buf[MAX_SOCKET_BUF_SIZE], *buf = recv_buf;

    int int_data_count = platform_client.int_data_count;
    int float_data_count = platform_client.float_data_count;
    int string_data_count = platform_client.string_data_count;

    char (*int_data_name)[MAX_NAME_SIZE] = platform_client.int_data_name;
    char (*float_data_name)[MAX_NAME_SIZE] = platform_client.float_data_name;
    char (*string_data_name)[MAX_NAME_SIZE] = platform_client.string_data_name;

    int *int_data_value = platform_client.int_data_value;
    float *float_data_value = platform_client.float_data_value;
    char (*string_data_value)[MAX_NAME_SIZE] = platform_client.string_data_value;

    if (!is_connected(platform_client.data_socket)) {
        eregec_pwarning("eregec_upload_data(): data not upload: Data Socket not connected!\n");
        return false;
    }

    buf += sprintf(buf, "Platform Data\n");
    for (int i = 0; i < int_data_count; i++) 
        buf += sprintf(buf, "%s:int:%d\n", int_data_name[i], int_data_value[i]);
    for (int i = 0; i < float_data_count; i++) 
        buf += sprintf(buf, "%s:float:%g\n", float_data_name[i], float_data_value[i]);
    for (int i = 0; i < string_data_count; i++) 
        buf += sprintf(buf, "%s:string:%s\n", string_data_name[i], string_data_value[i]);
    buf += sprintf(buf, "End\n");
    return send_string(DATA_SOCKET, recv_buf);
}
