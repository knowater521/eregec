# Java语言接口

### 介绍
为了方便客户端的开发，本项目提供了对客户端的连接协议做了一个基于Java的封装，屏蔽了客户端与服务器之间的连接协议。  
提供本代码的目的是方便用户使用Java语言快速的开发本服务器的客户端，如Android App或者基于Java的PC端。

### 代码
此Java客户端API代码位于[源码](https://github.com/mxb360/eregec)树的[client/java/api/](https://github.com/mxb360/eregec/blob/master/client/java/api)目录里。  
* [src/](https://github.com/mxb360/eregec/blob/master/client/java/api/src)便是代码实现；  
* [lib/](https://github.com/mxb360/eregec/blob/master/client/java/api/lib)里是用到的第三方jar包：本项目使用了org.json包来解析JSON数据。  


### 快速开始
将src里的源码和lib里的jar包添加到你的Java项目里

#### 使用方法
* 导包：`import com.mxb360.eregec;`
* 创建Eregec实例：`Eregec eregec = new Eregec(服务器域名 或者 IP:端口);`
* 登录：`eregec.login(用户名, 密码)`
* 从服务器更新平台数据：`eregec.updatePlatformData()`
* 取出需要的数据，如温度：`float temperature = eregec.getFloatData("temperature")`
* 向硬件平台发送命令：`eregec.sendCmd(命令字符串)`
* 用户登出：`eregec.logout()`


#### 示例代码

这里通过一个完整而详细的例子说明本API的使用。

```java
/* 实现一个命令行客户端，用户通过相应指令来控制客户端：
 * 软件启动时让用户输入用户名和密码，登录服务器
 * 登录成功后然后循环地让用户输入相关命令，执行相关操作：
 *   输入print：打印平台数据
 *   输入cmd xxx： 将xxx当做命令发给硬件平台让硬件平台执行
 *   输入exit： 用户登出并退出
 */

import com.mxb360.eregec.Eregec;     // 导入Eregec
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
        Eregec eregec = new Eregec("mxb360.top");

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
            switch (getInputString(">>> ").trim()) {
            case "print":
                /* 更新平台数据
                 * updatePlatformData方法用于重服务器获取平台数据，如果失败，返回false
                 * getFloatData获取float类型的数据
                 */
                if (eregec.updatePlatformData()) {
                    System.out.println("平台数据：");
                    System.out.println("    温度：" + eregec.getFloatData("temperature"))
                } else 
                    System.out.println("错误：平台数据获取失败：" + eregec.getErrorMessage());
                break;
            case "exit":
                isRunning = false;
                break;
            default:
                System.out.println("错误：未知操作！");
                break;
            }
        }

        /* 退出系统 
         * logout用于退出系统，失败返回false
         */
        if (eregec.logout())
            System.out.println("错误：登出系统失败：" + eregec.getErrorMessage());
    }
}
```
