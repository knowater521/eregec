package com.mxb360.eregec;

import java.util.Scanner;

public class Main {
    private static String getInput(String string) {
        System.out.print(string + ": ");
        Scanner scanner = new Scanner(System.in);
        return scanner.nextLine();
    }

    public static void main(String[] args) {
        Eregec eregec = new Eregec("http://39.108.3.243:51433");

        // 登录
        System.out.println("-- 用户登录 --");
        String name = getInput("用户名");
        String password = getInput("密码");

        if (!eregec.login(name, password)) {
            System.out.println("登录失败：" + eregec.getErrorMessage());
            System.exit(0);
        } else
            System.out.println("登录成功：用户id：" + eregec.getUserId());
    }
}
