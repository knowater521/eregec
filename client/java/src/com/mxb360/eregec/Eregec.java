package com.mxb360.eregec;

import com.mxb360.http.HttpClient;
import org.json.JSONException;
import org.json.JSONObject;

class JsonResult {
    String httpResult = "";
    String message = "";
    String errorMessage = "";
    String details = "";
    int code = -1;
    JSONObject data = null;

     JsonResult(String httpResult) {
        this.httpResult = httpResult;

        JSONObject jsonObject = new JSONObject(httpResult);
        code = jsonObject.getInt("code");
        message = jsonObject.getString("message");
        data = jsonObject.getJSONObject("data");
        details = code > 0 ?  data.getString("details") : null;
        errorMessage = code > 0 ? message + ": " + details : "";
    }

    Integer getIntData(String name) {
        if (code != 0)
            return null;
        try {
            return data.getInt(name);
        } catch (JSONException e) {
            errorMessage = e.toString();
            return null;
        }
    }

    Float getFloatData(String name) {
        if (code != 0)
            return null;
        try {
            return data.getFloat(name);
        } catch (JSONException e) {
            errorMessage = e.toString();
            return null;
        }
    }

    String getStringData(String name) {
        if (code != 0)
            return null;
        try {
            return data.getString(name);
        } catch (JSONException e) {
            errorMessage = e.toString();
            return null;
        }
    }
}

public class Eregec {
    private String errorMessage = "";
    private String userId = null;
    private String host;
    private JsonResult platformJsonResult = null;

    public Eregec(String host) {
        this.host = "http://" + host + "/eregec/api/";
    }

    private JsonResult post(HttpClient httpClient)   {
        String res = httpClient.post();
        if (res.equals("")) {
            errorMessage = httpClient.getErrorMessage();
            return null;
        }

        JsonResult jsonResult = new JsonResult(res);
        if (jsonResult.code != 0) {
            errorMessage = jsonResult.errorMessage;
            return null;
        }

        return jsonResult;
    }

    private JsonResult userPost(HttpClient httpClient) {
        if (userId == null) {
            errorMessage = "user not login";
            return null;
        }

        httpClient.addParam("userid", userId);
        return post(httpClient);
    }

    public boolean login(String userName, String password) {
        HttpClient loginHttpClient = new HttpClient(host + "login");
        loginHttpClient.addParam("name", userName);
        loginHttpClient.addParam("password", password);
        JsonResult loginJsonResult = post(loginHttpClient);
        if (loginJsonResult == null)
            return false;
        userId = loginJsonResult.getStringData("userid");
        if (userId == null)
            return false;
        downloadPlatformData();
        return true;
    }

    public void logout() {
        userPost(new HttpClient(host + "logout"));
        userId = null;
    }

    public boolean isLogin() {
        return userId != null;
    }

    public String getUserId() {
        return userId != null ? userId : "";
    }

    public Integer getIntegerPlatformData(String name) {
        if (platformJsonResult == null)
            downloadPlatformData();
        if (platformJsonResult == null)
            return null;
        Integer data = platformJsonResult.getIntData(name);
        if (data == null)
            errorMessage = platformJsonResult.errorMessage;
        return data;
    }

    public Float getFloatPlatformData(String name) {
        if (platformJsonResult == null)
            downloadPlatformData();
        if (platformJsonResult == null)
            return null;
        Float data = platformJsonResult.getFloatData(name);
        if (data == null)
            errorMessage = platformJsonResult.errorMessage;
        return data;
    }

    public String getStringPlatformData(String name) {
        if (platformJsonResult == null)
            downloadPlatformData();
        if (platformJsonResult == null)
            return null;
        String data = platformJsonResult.getStringData(name);
        if (data == null)
            errorMessage = platformJsonResult.errorMessage;
        return data;
    }

    public UserInformation getUserInformation() {
        return null;
    }

    public PlatformInformation getPlatformInformation() {

        return null;
    }

    public boolean sendCommand(String command) {
        HttpClient httpClient = new HttpClient(host + "cmd");
        httpClient.addParam("string", command.trim());
        return userPost(httpClient) != null;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public boolean downloadPlatformData() {
        platformJsonResult = userPost(new HttpClient(host + "platform-data"));
            return platformJsonResult != null;
    }
}
