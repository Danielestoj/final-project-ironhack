import { describe, it, expect, afterEach, vi } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";

vi.mock("../api/auth", () => ({
  login: vi.fn(() => Promise.resolve({ access_token: "x", usuario: {} })),
  register: vi.fn(() => Promise.resolve({ access_token: "x", usuario: {} })),
  logout: vi.fn(),
  getToken: vi.fn(() => null),
  getUser: vi.fn(() => null),
}));

import { AuthProvider } from "../context/AuthContext";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";

afterEach(cleanup);

function renderWithProviders(component) {
  return render(
    <BrowserRouter>
      <AuthProvider>{component}</AuthProvider>
    </BrowserRouter>
  );
}

describe("LoginPage", () => {
  it("renders login form title", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByText("Iniciar sesión")).toBeDefined();
  });

  it("renders submit button", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByRole("button", { name: /Entrar/i })).toBeDefined();
  });

  it("renders registration link", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByText(/Regístrate/)).toBeDefined();
  });
});

describe("RegisterPage", () => {
  it("renders title", () => {
    renderWithProviders(<RegisterPage />);
    expect(screen.getByText("Crear cuenta")).toBeDefined();
  });

  it("renders submit button", () => {
    renderWithProviders(<RegisterPage />);
    expect(screen.getByRole("button", { name: /Registrarse/i })).toBeDefined();
  });
});
