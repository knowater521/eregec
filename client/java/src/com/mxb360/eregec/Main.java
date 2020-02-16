/* 实现一个命令行客户端，用户通过相应指令来控制客户端：
 * 软件启动时让用户输入用户名和密码，登录服务器
 * 登录成功后然后循环地让用户输入相关命令，执行相关操作：
 *   输入print：打印平台数据
 *   输入cmd xxx： 将xxx当做命令发给硬件平台让硬件平台执行
 *   输入exit： 用户登出并退出
 */
package com.mxb360.eregec;
import java.util.Scanner;

public class Main {
    // 封装一个输入，简化输入相关代码
    private static String getInputString(String string) {
        System.out.print(string);
        Scanner scanner = new Scanner(System.in);
        return scanner.nextLine();
    }

    public static void main(String[] args) {
        /* 创建一个Eregec对象
         * Eregec对象用于完成客户端和服务器之间的通信
         * 创建Eregec需要指定访问服务器的域名
         */
        Eregec eregec = new Eregec("39.108.3.243:51433");

        // 从输入获取用户名和密码
        String name = getInputString("用户名: ");
        String password = getInputString("密码: ");

        /* 用户登录
         * login方法用于登录服务器，参数是用户名和密码
         * 如果登录成功，login方法返回true，否则返回false
         * 如果登录失败，可以通过getErrorMessage方法获取失败原因的字符串描述
         * 如果登录成功，可以通过getUserId()拿到服务器返回的用户ID
         * 对于使用了本库来说，用户ID并不重要。
         */
        if (!eregec.login(name, password)) {
            System.out.println("错误：登录失败：" + eregec.getErrorMessage());
            System.exit(0);
        } else
            System.out.println("登录成功：用户id：" + eregec.getUserId());

        boolean isRunning = true;
        while (isRunning) {
            String[] commands = getInputString(">>> ").trim().split(" ");
            switch (commands[0]) {
                case "print":
                    /* 更新平台数据
                     * updatePlatformData方法用于重服务器获取平台数据，如果失败，返回false
                     * getFloatData获取float类型的数据
                     */
                    if (eregec.downloadPlatformData()) {
                        System.out.println("平台数据：");
                        System.out.println("    温度：" + eregec.getFloatPlatformData("temperature"));
                        System.out.println("    湿度：" + eregec.getFloatPlatformData("humidity"));
                    } else
                        System.out.println("错误：平台数据获取失败：" + eregec.getErrorMessage());
                    break;
                case "cmd":
                    if (commands.length > 1) {
                        /* 发送命令到硬件平台
                         * sendCommand(命令字符串)
                         */
                        if (!eregec.sendCommand(commands[1]))
                            System.out.println("错误：命令执行失败：" + eregec.getErrorMessage());
                    } else
                        System.out.println("错误：cmd: 命令缺少参数");
                    break;
                case "exit":
                    isRunning = false;
                    break;
                default:
                    System.out.println("错误：" + commands[0] + ": 未知操作");
                    break;
            }
        }

        /* 退出系统 */
        eregec.logout();
    }
}