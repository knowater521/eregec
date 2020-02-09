package com.mxb360.eregec;

import com.mxb360.http.HttpClient;

class User {
    String name = null;
    String password = null;
    String id = null;

    public User(String name, String password) {
        this.name = name;
        this.password = password;
        this.id = "";
    }
}

public class Eregec {
    private HttpClient loginHttpClient = null;
    private String errorMessage = "";

    private String host = null;
    private LoginJsonResult loginJsonResult;

    public Eregec(String host) {
        this.host = host;

        loginHttpClient = new HttpClient(host + "/eregec/api/login");
    }

    public boolean login(String userName, String password) {
        loginHttpClient.clearParam();
        loginHttpClient.addParam("name", userName);
        loginHttpClient.addParam("password", password);
        String res = loginHttpClient.post();
        if (res.equals(""))
            errorMessage = loginHttpClient.getErrorMessage();

        loginJsonResult = new LoginJsonResult(res, errorMessage);
        errorMessage = loginJsonResult.isOk() ? "no error" : loginJsonResult.getErrorMessage();
        return loginJsonResult.isOk();
    }

    public boolean loginOk() {
        return loginJsonResult != null && loginJsonResult.isOk();
    }

    public LoginJsonResult getLoginJsonResult() {
        return loginJsonResult;
    }

    public String getUserId() {
        return loginOk() ? loginJsonResult.getUserId() : "";
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}
