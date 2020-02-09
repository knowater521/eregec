package com.mxb360.eregec;

public class LoginJsonResult extends JsonResult {
    private String userId = "";

    public LoginJsonResult(String httpResult, String error) {
        super(httpResult, error);
        if (isOk())
            userId = data.getString("userid");
    }

    public String getUserId() {
        return userId;
    }
}
