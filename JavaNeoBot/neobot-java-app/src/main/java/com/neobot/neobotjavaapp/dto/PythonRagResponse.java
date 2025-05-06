package com.neobot.neobotjavaapp.dto;

// Represents the JSON body {"answer": "...", "error": "..."} received FROM the Python API
public class PythonRagResponse {
    private String answer;
    private String error;

    // Default constructor
    public PythonRagResponse() {
    }

    // Getters and Setters
    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Optional: toString for easy logging
    @Override
    public String toString() {
        return "PythonRagResponse{" +
                "answer='" + (answer != null ? answer.substring(0, Math.min(answer.length(), 50)) + "..." : "null") + '\'' + // Log snippet
                ", error='" + error + '\'' +
                '}';
    }
}