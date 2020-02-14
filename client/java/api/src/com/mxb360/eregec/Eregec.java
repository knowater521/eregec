package com.mxb360.eregec;

import com.mxb360.http.HttpClient;

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

    public boolean isLogin() {
        return loginJsonResult != null && loginJsonResult.isOk();
    }

    public LoginJsonResult getLoginJsonResult() {
        return loginJsonResult;
    }

    public String getUserId() {
        return isLogin() ? loginJsonResult.getUserId() : "";
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}
