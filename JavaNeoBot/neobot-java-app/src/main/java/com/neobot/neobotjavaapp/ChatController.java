package com.neobot.neobotjavaapp; // Make sure this matches your actual package name!

// Removed FeedbackRequest import
import com.neobot.neobotjavaapp.dto.PythonRagResponse;
import com.neobot.neobotjavaapp.service.RAGServiceClient;
import org.slf4j.Logger; // Import Logger
import org.slf4j.LoggerFactory; // Import LoggerFactory
// Removed ResponseEntity import
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
// Removed PostMapping import
// Removed RequestBody import
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import reactor.core.publisher.Mono; // Import Mono

@Controller
public class ChatController {

    private static final Logger log = LoggerFactory.getLogger(ChatController.class); // Logger for controller

    private final RAGServiceClient ragServiceClient;

    // Constructor injection for the service client
    public ChatController(RAGServiceClient ragServiceClient) {
        this.ragServiceClient = ragServiceClient;
    }

    // Endpoint to serve the main HTML chat page
    @GetMapping("/chat")
    public String showChatPage() {
        log.info("Serving the chat page (/chat)...");
        return "chat"; // Returns the name of the template: chat.html
    }

    // Endpoint to redirect root path "/" to "/chat"
    @GetMapping("/")
    public String redirectToChat() {
        log.info("Redirecting root path (/) to /chat...");
        return "redirect:/chat";
    }

    // API endpoint called by the JavaScript in chat.html to get RAG answer
    // Handles GET requests to /api/ask?question=YourQuestionHere
    // Returns a Mono which Spring WebFlux handles asynchronously
    @GetMapping("/api/ask")
    @ResponseBody // Return data directly as JSON, not an HTML view name
    public Mono<PythonRagResponse> askRagApi(@RequestParam String question) {
        log.info("Received ASYNC API ask request for: '{}'", question);

        // Call the asynchronous service method which returns a Mono
        Mono<PythonRagResponse> responseMono = ragServiceClient.getRagResponseAsync(question);

        // Add logging for when the async operation completes (optional, good for debugging)
        return responseMono.doOnSuccess(response -> {
            // Log snippet of answer or error for brevity
            String logAnswer = (response != null && response.getAnswer() != null)
                    ? response.getAnswer().substring(0, Math.min(response.getAnswer().length(), 70)) + "..."
                    : "null";
            String logError = (response != null) ? response.getError() : "response was null";
            log.info("Async RAG call completed. Returning response: Answer='{}', Error='{}'", logAnswer, logError);
        }).doOnError(error -> {
            // Log errors that occur during the Mono processing itself
            log.error("Async RAG call failed in controller processing phase: {}", error.getMessage());
        });
        // Spring WebFlux subscribes to the Mono and writes the result to the HTTP response when available
    }

    // --- REMOVED FEEDBACK ENDPOINT ---
    // @PostMapping("/api/feedback")
    // public ResponseEntity<String> handleFeedback(@RequestBody FeedbackRequest feedback) { ... }
    // --- END REMOVED FEEDBACK ENDPOINT ---
}