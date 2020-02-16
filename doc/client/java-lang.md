# Java语言接口

### 介绍
为了方便客户端的开发，本项目提供了对客户端的连接协议做了一个基于Java的封装，屏蔽了客户端与服务器之间的连接协议。(封装服务器的HTTP协议)  
提供本代码的目的是方便用户使用Java语言快速的开发本服务器的客户端，如Android App或者基于Java的PC端。

### 代码
此Java客户端API代码位于[源码](https://github.com/mxb360/eregec)树的[client/java/](https://github.com/mxb360/eregec/blob/master/client/java)目录里。  
* [src/](https://github.com/mxb360/eregec/blob/master/client/java/src)便是代码实现；  
* [lib/](https://github.com/mxb360/eregec/blob/master/client/java/lib)里是用到的第三方jar包：本项目使用了org.json包来解析JSON数据。  


### 快速开始
将src里的源码和lib里的jar包添加到你的Java项目里

#### 使用方法
* 导包：`import com.mxb360.eregec.Eregec;`
* 创建Eregec实例：`Eregec eregec = new Eregec(服务器域名 或者 IP:端口);`
* 登录：`eregec.login(用户名, 密码)`
* 从服务器更新平台数据：`eregec.downloadPlatformData()`
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
import com.mxb360.eregec.Eregec;              // 导入Eregec
import com.mxb360.eregec.UserInformation;     // 导入UserInformation
import com.mxb360.eregec.PlatformInformation; // 导入PlatformInformation
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
            String[] commands = getInputString(">>> ").trim().split(" ");
            switch (commands[0]) {
            case "print":
                /* 更新平台数据
                 * downloadPlatformData方法用于重服务器获取平台数据，如果失败，返回false
                 * getFloatPlatformData方法获取float类型的数据
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
```

### 所有API

#### Class Eregec:

#### Eregec(String host)
* 参数：
    * host: 服务器域名或者IP:端口
* 功能：
    * 构造器

#### boolean login(String userName, String password)
* 参数：
    * userName: 用户名
    * password: 密码
* 功能:
    * 用户登录服务器
* 返回：
    * 登录成功返回true，失败返回false（可用getErrorMessage()获取失败原因字符串描述）

#### void logout()
* 参数：
    * 无
* 功能:
    * 用户登出
* 返回：
    * 无

#### String getUserId() 
* 参数：无
* 功能：
    * 获取用户ID
* 返回：
    * 返回用户ID，失败返回null（可用getErrorMessage()获取失败原因字符串描述）

#### String getErrorMessage() 
* 参数：无
* 功能：
    * 获取错误信息描述
* 返回：
    * 错误信息描述字符串

#### Integer getIntegerPlatformData(String name) 
* 参数：
*   name: 数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * 返回相应数据，失败返回null（可用getErrorMessage()获取失败原因字符串描述）

#### Float getFloatPlatformData(String name) 
* 参数：
*   name: 数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * 返回相应数据，失败返回null（可用getErrorMessage()获取失败原因字符串描述）

#### String getStringPlatformData(String name) 
* 参数：
*   name: 数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * 返回相应数据，失败回null（可用getErrorMessage()获取失败原因字符串描述）

#### PlatformInformation getPlatformInformation() 
* 参数：
*   无
* 功能：
    * 获取平台信息
* 返回：
    * 返回平台信息（可用getErrorMessage()获取失败原因字符串描述）

#### UserInformation getUserInformation() 
* 参数：
*   无
* 功能：
    * 获取用户信息
* 返回：
    * 返回用户信息（可用getErrorMessage()获取失败原因字符串描述）

#### boolean isLogin()
* 参数：无
* 功能：
    * 判断当前是否登录状态
* 返回：
    * 如果处于登录状态，返回true，否则返回false

#### boolean sendCommand(String command)
* 参数：
    * command: 命令字符串
* 功能：
    * 向平台发送指定命令
* 返回：
    * 成功返回true，失败返回false（可用getErrorMessage()获取失败原因字符串描述）

#### boolean downloadPlatformData()
* 参数：
    * 无
* 功能：
    * 下载更新平台数据
* 返回：
    * 成功返回true，失败返回false（可用getErrorMessage()获取失败原因字符串描述）