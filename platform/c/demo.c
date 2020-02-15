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
    } else if (!strcmp(cmd, "open-led")) {
        printf("关灯！\n");
    } else {
        printf("%s: 不能识别的命令\n", cmd);
        return COMMAND_FAILED("unkown command!");
    }
    return COMMAND_OK("OK");
}

int main(void)
{
    signal(SIGINT, stop_by_ctrl_c);

    eregec_init("mxb-platform", "mxb", "39.108.3.243", 51435);

    if (!eregec_connect()) {
        printf("Error: Connect Server Failed!\n");
        return 1;
    }

    eregec_set_cmd_callback(resolve_command);

    while (eregec_is_connected()) {
        eregec_set_float_data("temperature", 37 + (rand() % 10) / 10.0);
        eregec_set_float_data("humidity", 18 + (rand() % 100)/ 100.0);
        eregec_upload_data();
        sleep(1);
    }

    printf("Warning: all socket broken.\n");
    eregec_disconnect();
	return 0;
}
