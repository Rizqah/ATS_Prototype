import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CandidatesPage, ReportsPage, TopNav } from "./App";

const workspace = {
  job_title: "Frontend Engineer",
  job_description: "Frontend Engineer\nReact and accessibility",
  candidates: [
    {
      name: "Ada Lovelace",
      title: "Engineer",
      company: "Analytical Engines",
      role: "Frontend Engineer",
      score: 88,
      status: "Shortlist",
      exp: "5y",
      source: "Referral",
    },
    {
      name: "Grace Hopper",
      title: "Engineer",
      company: "Compiler Labs",
      role: "Frontend Engineer",
      score: 72,
      status: "Reviewing",
      exp: "4y",
      source: "Uploaded CV",
    },
  ],
};

function captureDownloads() {
  const blobs = [];
  vi.stubGlobal("URL", {
    createObjectURL: vi.fn((blob) => {
      blobs.push(blob);
      return "blob:test-download";
    }),
    revokeObjectURL: vi.fn(),
  });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
  return blobs;
}

describe("hiring reports", () => {
  beforeEach(() => captureDownloads());

  it("starts with the four core recruitment metrics and supports clearing them", async () => {
    const user = userEvent.setup();
    render(<ReportsPage workspace={workspace} />);

    expect(screen.getByText("4 metrics selected")).toBeInTheDocument();
    const selectedMetrics = document.querySelector(".selected-report-metrics");
    expect(within(selectedMetrics).getByText("Time to fill")).toBeInTheDocument();
    expect(within(selectedMetrics).getByText("Quality of hire")).toBeInTheDocument();

    await user.click(screen.getByText("4 metrics selected"));
    await user.click(screen.getByRole("button", { name: "Clear" }));

    expect(screen.getByText("Choose metrics")).toBeInTheDocument();
    expect(document.querySelector(".selected-report-metrics")).not.toBeInTheDocument();
  });

  it("exports the hiring report as a PDF", async () => {
    const user = userEvent.setup();
    render(<ReportsPage workspace={workspace} />);

    await user.click(screen.getByRole("button", { name: "Export PDF" }));

    expect(URL.createObjectURL).toHaveBeenCalledOnce();
    expect(URL.createObjectURL.mock.calls[0][0].type).toBe("application/pdf");
    const link = document.querySelector('a[download="fydara-hiring-report.pdf"]');
    expect(link).not.toBeInTheDocument();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalledOnce();
  });
});

describe("talent pool", () => {
  it("filters candidates and exports only when results exist", async () => {
    captureDownloads();
    const user = userEvent.setup();
    render(<CandidatesPage workspace={workspace} onOpenReport={vi.fn()} />);

    const exportButton = screen.getByRole("button", { name: "Export pool" });
    expect(screen.getByText("2 candidates shown")).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("Search name, role, company..."), "Ada");
    expect(screen.getByText("1 candidate shown")).toBeInTheDocument();
    expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();

    await user.click(exportButton);
    expect(URL.createObjectURL.mock.calls[0][0].type).toBe("text/csv;charset=utf-8");

    await user.clear(screen.getByPlaceholderText("Search name, role, company..."));
    await user.type(screen.getByPlaceholderText("Search name, role, company..."), "Nobody");
    expect(exportButton).toBeDisabled();
    expect(within(screen.getByText("No candidates found").parentElement).getByText(/Adjust the search/)).toBeInTheDocument();
  });
});

describe("mobile navigation", () => {
  it("makes every recruiter page and account action reachable from the menu", async () => {
    const user = userEvent.setup();
    const setPage = vi.fn();
    render(<TopNav page="recruiter" role="recruiter" setPage={setPage} onLogout={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Open navigation" }));

    expect(screen.getByRole("button", { name: /Workspace/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Profile/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Candidates/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Reports/ })).toBeInTheDocument();
    expect(within(screen.getByRole("navigation", { name: "Primary navigation" })).getByRole("button", { name: "Security" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Profile/ }));
    expect(setPage).toHaveBeenCalledWith("recruiter-profile");
    expect(screen.getByRole("button", { name: "Open navigation" })).toHaveAttribute("aria-expanded", "false");
  });
});
