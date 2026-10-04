import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { randomUUID } from "crypto";

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

        const cookieStore = await cookies();
        let sessionId = cookieStore.get("portfolio_session_id")?.value;

        if (!sessionId) {
            sessionId = randomUUID();
        }

        const response = await fetch(`${apiUrl}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ...body,
                session_id: sessionId,
            }),
        });

        const data = await response.json();

        const nextResponse = NextResponse.json(data, {
            status: response.status,
        });

        if (!cookieStore.get("portfolio_session_id")) {
            nextResponse.cookies.set("portfolio_session_id", sessionId, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                path: "/",
                maxAge: 60 * 60 * 24 * 30,
            });
        }

        return nextResponse;
    } catch (error) {
        console.error("PortfolioPilot API proxy error:", error);

        return NextResponse.json(
            { error: "Unable to reach the AI backend." },
            { status: 502 }
        );
    }
}
