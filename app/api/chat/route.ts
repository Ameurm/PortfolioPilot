import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const apiUrl = process.env.API_URL;

        if (!apiUrl) {
            return NextResponse.json(
                { error: "API_URL environment variable is not configured." },
                { status: 500 }
            );
        }

        const response = await fetch(`${apiUrl}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        return NextResponse.json(data, {
            status: response.status,
        });
    } catch (error) {
        console.error("PortfolioPilot API proxy error:", error);

        return NextResponse.json(
            { error: "Unable to reach the AI backend." },
            { status: 502 }
        );
    }
}
