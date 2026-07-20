import LoginPage from "../pages/LoginPage";

describe("Login Automation", () => {

  it("logs in successfully with valid credentials", () => {
    LoginPage.visit();               // Navigation
    LoginPage.fillUsername("tomsmith");
    LoginPage.fillPassword("SuperSecretPassword!");
    LoginPage.submit();              // Form submission

    cy.get(".flash.success")         // Validation
      .should("be.visible")
      .and("contain", "You logged into a secure area");
  });

  it("shows an error with invalid credentials", () => {
    LoginPage.visit();
    LoginPage.fillUsername("wronguser");
    LoginPage.fillPassword("wrongpass");
    LoginPage.submit();

    cy.get(".flash.error")           // Validation
      .should("be.visible")
      .and("contain", "Your username is invalid");
  });

});