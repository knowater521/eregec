#include <stdio.h>
#include <stdlib.h>

#include "eregec.h"

int main(void)
{
    eregec_init("mxb-platform", "mxb", "39.108.3.243", 51435);
    if (!eregec_connect()) {
        printf("Error: Connect Server Failed!\n");
    }

    eregec_disconnect();
	return 0;
}
