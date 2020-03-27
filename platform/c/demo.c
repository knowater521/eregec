#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

/* Linux sleep */
#ifdef __linux
#include <unistd.h>
#endif

/* Win32 sleep */
#ifdef _WIN32
#include <Windows.h>
#define sleep(s)   Sleep((s)*1000)
#endif

#include "eregec.h"

void stop_by_ctrl_c(int sig)
{
    eregec_disconnect();
    printf("\nStop By Ctrl-C\n");
    exit(0);
}

const char *resolve_command(const char *cmd)
{
    if (!strcmp(cmd, "open-led")) {
        printf("开灯！\n");
    } else if (!strcmp(cmd, "close-led")) {
        printf("关灯！\n");
    } else {
        printf("%s: 不能识别的命令\n", cmd);
        return COMMAND_FAILED("unkown command!");
    }
    return COMMAND_OK("succeed!");
}

int main(int argc, char *argv[])
{
#if 0
    char name[128] = "eregec";
    char password[128] = "123456";
    const char *arg;

    #define have_cmd(s1, s2)        !strcmp(argv[i], s1) || !strcmp(argv[i], s2)
    #define get_arg(i)              (i + 1 < argc && argv[i+1][0] != '-') ? argv[++i] : NULL
    #define exit_cmdline_error(...) do {printf("Error: " __VA_ARGS__); exit(1);} while (0)

    for (int i = 1; i < argc; i++) {
        if (have_cmd("-n", "--name")) {
            if ((arg = get_arg(i)))
                strcpy(name, arg);
            else 
                exit_cmdline_error("%s: 缺少参数。尝试：--help。\n", argv[i]);
        } else if (have_cmd("-p", "--password")) {
            if ((arg = get_arg(i)))
                strcpy(password, arg);
            else
                exit_cmdline_error("%s: 缺少参数。尝试：--help。\n", argv[i]);
        } else if (have_cmd("-h", "--help")) {
            printf("用法：\n    %s [选项]\n选项：\n", argv[0]);
            puts("    -n, --name NAME          指定用户名为NAME");
            puts("    -p, --password PASSWORD  指定用户密码为PASSWORD");
            puts("    -h, --help               显示此信息后退出");
            exit(0);
        } else
            exit_cmdline_error("%s: 未知选项。尝试：--help。\n", argv[i]);
    }
#endif

    eregec_init("eregec", "123456", "39.108.3.243", 51435);

    if (!eregec_connect()) {
        printf("Error: Connect Server Failed!\n");
        return 1;
    }

    eregec_set_command_callback(resolve_command);

    signal(SIGINT, stop_by_ctrl_c);
    while (eregec_is_connected()) {
        //if (eregec_is_data_socket_connected()) {
            eregec_set_float_data("temperature", 37 + (rand() % 10) / 10.0);
            eregec_set_float_data("humidity", 18 + (rand() % 100)/ 100.0);
            eregec_upload_data();
        //}
        sleep(1);
    }

    printf("Warning: all socket broken.\n");
    eregec_disconnect();
    return 0;
}
