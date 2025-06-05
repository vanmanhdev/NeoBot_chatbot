package com.neobot.neobotjavaapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
// import org.springframework.web.client.RestTemplate; // Can remove this line
import org.springframework.web.reactive.function.client.WebClient; // Import WebClient

@SpringBootApplication
public class NeobotJavaAppApplication {

	public static void main(String[] args) {
		SpringApplication.run(NeobotJavaAppApplication.class, args);
	}
	@Bean
	public WebClient webClient(WebClient.Builder builder) {
		return builder.build();
	}
}