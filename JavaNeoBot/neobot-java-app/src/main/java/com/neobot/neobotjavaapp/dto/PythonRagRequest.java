package com.neobot.neobotjavaapp.dto;

// Represents the JSON body {"question": "..."} sent TO the Python API
public class PythonRagRequest {
    private String question;

    // Need default constructor for JSON mapping
    public PythonRagRequest() {
    }

    public PythonRagRequest(String question) {
        this.question = question;
    }

    // Getters and Setters are needed for JSON mapping libraries
    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }
}