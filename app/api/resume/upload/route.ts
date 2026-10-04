import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { randomUUID } from "crypto";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
    try {
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

        const incomingFormData = await request.formData();
        const file = incomingFormData.get("file");

        if (!(file instanceof File)) {
            return NextResponse.json(
                { error: "No resume file was provided." },
                { status: 400 }
            );
        }

        const backendFormData = new FormData();
        backendFormData.append("file", file, file.name);
        backendFormData.append("session_id", sessionId);

        const backendResponse = await fetch(
            `${apiUrl.replace(/\/$/, "")}/resume/upload`,
            {
                method: "POST",
                body: backendFormData,
            }
        );

        const responseText = await backendResponse.text();

        let responseData: unknown;

        try {
            responseData = JSON.parse(responseText);
        } catch {
            responseData = { detail: responseText };
        }

        const nextResponse = NextResponse.json(responseData, {
            status: backendResponse.status,
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
        console.error("Resume upload proxy error:", error);

        return NextResponse.json(
            { error: "Unable to upload resume to the AI backend." },
            { status: 500 }
        );
    }
}
