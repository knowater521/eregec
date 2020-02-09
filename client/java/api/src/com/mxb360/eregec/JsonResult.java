package com.mxb360.eregec;

import org.json.JSONObject;

public class JsonResult {
    private String httpResult = "";
    private String message = "";
    private String errorMessage = "";
    private String details = "";
    private int code = -1;
    protected JSONObject data = null;

    public JsonResult(String httpResult, String error) {
        if (error == null || !error.equals("")) {
            errorMessage = "http error: " + error;
            return;
        }

        this.httpResult = httpResult;

        JSONObject jsonObject = new JSONObject(httpResult);
        code = jsonObject.getInt("code");
        message = jsonObject.getString("message");
        data = jsonObject.getJSONObject("data");
        details = code > 0 ?  data.getString("details") : null;
        errorMessage = code > 0 ? message + ": " + details : "no error";
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public String getDetails() {
        return details;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public boolean isOk() {
        return code == 0;
    }

    @Override
    public String toString() {
        return httpResult;
    }
}
