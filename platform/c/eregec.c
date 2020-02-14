#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include <errno.h>

#ifdef __linux

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

typedef int socket_t;

#define closesocket close

#define socket_init()       ((void)0)  
#define get_socket_error()  strerror(errno) 

#endif

#ifdef  _WIN32
#include <WinSock2.h>
#include <Ws2tcpip.h>

#ifdef _MSC_VER 
#pragma comment(lib, "Ws2_32.lib")
#endif

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

#endif

#include "eregec.h"

#define eregec_perror(...)    printf("PlatformClient: Error: " __VA_ARGS__)
#define eregec_pwarning(...)  printf("PlatformClient: Warning: " __VA_ARGS__)
#define eregec_pinfo(...)     printf("PlatformClient: Info: " __VA_ARGS__)
#define BAD_SOCKET            (socket_t)0

#define MAX_ID_SIZE 1023
#define MAX_NAME_SIZE 1023
#define MAX_HOST_SIZE 1023
#define MAX_ERROR_SIZE 1023
#define MAX_SOCKET_BUF_SIZE 4095

struct {
    char id[MAX_ID_SIZE + 1];
    char name[MAX_NAME_SIZE + 1];
    char host[MAX_HOST_SIZE + 1];
    int port;

    socket_t data_socket;
    socket_t command_socket;

    const char *(*callback_func)(const char *);

    char error_message_buf[MAX_ERROR_SIZE + 1];
} platform_client;

static socket_t connect_socket(const char *socket_name)
{
    socket_t fd; 
    char recv_buf[MAX_SOCKET_BUF_SIZE + 1];
    struct sockaddr_in servaddr;
    char *host = platform_client.host;
    int port = platform_client.port;

    eregec_pinfo("%s: Try to connect server %s:%d\n", socket_name, host, port);
    if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        eregec_perror("%s connect faild: socket(): %s\n", socket_name, get_socket_error());
        return BAD_SOCKET;
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &servaddr.sin_addr) <= 0) {
        eregec_perror("%s connect faild: inet_pton(): %s\n", socket_name, get_socket_error());
        return BAD_SOCKET;
    }
    if (connect(fd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
        eregec_perror("%s connect failed: connect(): %s\n", socket_name, get_socket_error());
        return BAD_SOCKET;
    }

    recv(fd, recv_buf, MAX_SOCKET_BUF_SIZE, 0);
    if (strcmp(recv_buf, "Electronic Ecological Estanciero Server")) {
        eregec_perror("%s connect failed: Bad Server Return", socket_name);
        return BAD_SOCKET;
    }
    eregec_pinfo("%s is connected\n", socket_name);

    return fd;
}

void eregec_init(const char *id, const char *name, const char *host, int port)
{
    assert(id != NULL);
    assert(name != NULL);
    assert(host != NULL);
    assert(port > 0 && port < 65536);

    strncpy(platform_client.id, id, MAX_ID_SIZE);
    strncpy(platform_client.name, name, MAX_NAME_SIZE);
    strncpy(platform_client.host, host, MAX_HOST_SIZE);
    platform_client.port = port;
}

bool eregec_connect(void)
{
    bool data_socket_ok = eregec_connect_data_socket();
    bool command_socket_ok = eregec_connect_command_socket();
    return data_socket_ok || command_socket_ok;
}

bool eregec_connect_command_socket(void)
{
    platform_client.data_socket = connect_socket("Command Socket");
    return platform_client.data_socket != BAD_SOCKET;
}

bool eregec_connect_data_socket(void)
{
    platform_client.command_socket = connect_socket("Data Socket");
    return platform_client.command_socket != BAD_SOCKET;
}

void eregec_disconnect(void)
{
    eregec_disconnect_data_socket();
    eregec_disconnect_command_socket();
}

void eregec_disconnect_command_socket(void)
{
    if (platform_client.command_socket != BAD_SOCKET) {
        closesocket(platform_client.command_socket);
        eregec_pinfo("Command Socket: close()\n");
    }
}

void eregec_disconnect_data_socket(void)
{
    if (platform_client.data_socket != BAD_SOCKET) {
        closesocket(platform_client.data_socket);
        eregec_pinfo("Data Socket: close()\n");
    }
}

const char *eregec_get_error_message(void)
{
    return platform_client.error_message_buf;
}

bool eregec_is_command_socket_connected(void)
{
    return platform_client.command_socket != BAD_SOCKET;
}

bool eregec_is_data_socket_connected(void)
{
    return platform_client.data_socket != BAD_SOCKET;
}

bool eregec_is_connected(void)
{
    return eregec_is_command_socket_connected() || eregec_is_data_socket_connected();
}

void eregec_set_cmd_callback(const char *(*callback_func)(const char *cmd))
{
    platform_client.callback_func = callback_func;
}

void eregec_set_int_data(const char *name, int value)
{

}

void eregec_set_float_data(const char *name, float value)
{

}

void eregec_set_string_data(const char *name, const char  *value)
{

}

bool eregec_upload_data(void)
{
    return false;
}
