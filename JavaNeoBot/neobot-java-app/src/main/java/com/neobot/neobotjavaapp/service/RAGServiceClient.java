package com.neobot.neobotjavaapp.service;

import com.neobot.neobotjavaapp.dto.PythonRagRequest;
import com.neobot.neobotjavaapp.dto.PythonRagResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType; // Import MediaType
import org.springframework.stereotype.Service;
// import org.springframework.web.client.RestClientException; // No longer needed for WebClient specific errors
// import org.springframework.web.client.RestTemplate; // No longer needed
import org.springframework.web.reactive.function.client.WebClient; // Import WebClient
import org.springframework.web.reactive.function.client.WebClientResponseException; // For WebClient HTTP errors
import reactor.core.publisher.Mono; // Import Mono for asynchronous result
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.time.Duration; // For timeouts

@Service
public class RAGServiceClient {

    private static final Logger log = LoggerFactory.getLogger(RAGServiceClient.class);

    // Inject WebClient instead of RestTemplate
    private final WebClient webClient;

    @Value("${rag.api.url}")
    private String ragApiUrl;

    // Timeout duration for the API call (e.g., 30 seconds)
    private static final Duration API_TIMEOUT = Duration.ofSeconds(600);

    // Constructor injection for WebClient
    public RAGServiceClient(WebClient webClient) {
        this.webClient = webClient;
    }

    // Method now returns a Mono<PythonRagResponse> - an asynchronous result
    public Mono<PythonRagResponse> getRagResponseAsync(String userQuestion) {
        log.info("Sending question ASYNC to RAG API at {}: '{}'", ragApiUrl, userQuestion);
        PythonRagRequest requestPayload = new PythonRagRequest(userQuestion);

        return webClient
                .post() // Start defining a POST request
                .uri(ragApiUrl) // Set the target URI
                .contentType(MediaType.APPLICATION_JSON) // Set the content type of the request body
                .bodyValue(requestPayload) // Set the request body (WebClient handles JSON conversion)
                .retrieve() // Execute the request and retrieve the response body
                .bodyToMono(PythonRagResponse.class) // Decode the response body to a Mono<PythonRagResponse>
                .timeout(API_TIMEOUT) // Apply a timeout to the operation
                .doOnSuccess(response -> { // Log on successful response (non-blocking)
                    log.info("Successfully received ASYNC response from RAG API: {}", response);
                    if (response != null && response.getError() != null && !response.getError().isEmpty()) {
                        log.warn("RAG API returned an error message (async): {}", response.getError());
                    } else if (response == null){
                        log.error("Received null response body from RAG API (async)");
                        // Note: Handling null response body might require onErrorResume below
                    }
                })
                .onErrorResume(error -> { // Handle errors during the async call
                    log.error("Error calling RAG API (async) at {}: {}", ragApiUrl, error.getMessage());
                    // Log details for specific WebClient errors
                    if (error instanceof WebClientResponseException webError) {
                        log.error("RAG API HTTP Status: {}, Response Body: {}", webError.getStatusCode(), webError.getResponseBodyAsString());
                    }
                    // Create an error response object to return within the Mono stream
                    PythonRagResponse errorResponse = new PythonRagResponse();
                    errorResponse.setError("Failed to communicate with the RAG service: " + error.getClass().getSimpleName()); // More generic error for user
                    return Mono.just(errorResponse); // Return the error response as a successful Mono completion
                });
    }
}