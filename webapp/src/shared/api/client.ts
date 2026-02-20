import axios from "axios"

function createClient() {
    const client = axios.create({
        baseURL: "http://127.0.0.1:8000", // TODO: read from env
        timeout: 10000,
        headers: {
            "Content-Type": "application/json",
        },
    });

    // TODO: interceptors

    return client;
}



export const client = createClient();