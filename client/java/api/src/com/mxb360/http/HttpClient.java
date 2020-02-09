package com.mxb360.http;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class HttpClient {
    private String url;
    private StringBuffer param = new StringBuffer();
    private HttpURLConnection connection = null;
    private InputStream inputStream = null;
    private OutputStream outputStream = null;
    private BufferedReader bufferedReader = null;

    private String errorMessage = "";
    private int responseCode;

    public HttpClient(String url) {
        this.url = url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public void addParam(String key, String value) {
        if (param.length() > 0)
            param.append('&');

        param.append(key);
        param.append('=');
        param.append(value);
    }

    public void clearParam() {
        param = new StringBuffer();
    }

    public String get() {
        return connect("GET");
    }

    public String post() {
        return connect("POST");
    }

    public int getResponseCode() {
        return responseCode;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    private String connect(String method) {
        String result = "";
        responseCode = 0;

        try {
            setConnect(method);
            outputStream = connection.getOutputStream();
            if (method.equals("POST"))
                outputStream.write(param.toString().getBytes());
            connection.connect();
            responseCode = connection.getResponseCode();
            if (responseCode == 200)
                result = getResult();
            else
                errorMessage = "Server returned HTTP response code: " + responseCode + " for URL: " + url;
        } catch (IOException e) {
            e.printStackTrace();
            errorMessage = e.toString();
        } finally {
            closeStream();
            connection.disconnect();
        }
        return result;
    }

    private void setConnect(String method) throws IOException {
        int connectTimeout = 15000;
        int readTimeout = 60000;

        if (method.equals("GET") && param.length() > 0)
            this.url += '?' + param.toString();
        connection = (HttpURLConnection) new URL(this.url).openConnection();
        connection.setRequestMethod(method);
        connection.setConnectTimeout(connectTimeout);
        connection.setReadTimeout(readTimeout);
        connection.setDoOutput(true);
        connection.setDoInput(true);

        if (method.equals("POST")) {
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestProperty("Authorization", "Bearer da3efcbf-0845-4fe3-8aba-ee040be542c0");
        }
    }

    private String getResult() throws IOException {
        inputStream = connection.getInputStream();
        bufferedReader = new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
        StringBuilder stringBuilder = new StringBuilder();
        String temp;

        while ((temp = bufferedReader.readLine()) != null)
            stringBuilder.append(temp);
        return stringBuilder.toString();
    }

    private void closeStream() {
        if (bufferedReader != null) {
            try {
                bufferedReader.close();
            } catch (IOException e) {
                e.printStackTrace();
                errorMessage = e.toString();
            } finally {
                bufferedReader = null;
            }
        }
        if (outputStream != null) {
            try {
                outputStream.close();
            } catch (IOException e) {
                e.printStackTrace();
                errorMessage = e.toString();
            } finally {
                outputStream = null;
            }
        }
        if (inputStream != null) {
            try {
                inputStream.close();
            } catch (IOException e) {
                e.printStackTrace();
                errorMessage = e.toString();
            } finally {
                inputStream = null;
            }
        }
    }
}
