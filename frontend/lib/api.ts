import axios from "axios";

// Ensure API URL doesn't have a trailing slash
const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export interface Lead {
    id: number;
    Name: string;
    Email: string | null;
    Company: string;
    Role: string;
    Intent: string;
    Status: string;
}

export const api = {
    startJob: async (role: string, industry: string) => {
        try {
            const response = await axios.post(`${API_URL}/start-job`, null, {
                params: { role, industry },
            });
            return response.data;
        } catch (error) {
            console.error("Error starting job:", error);
            throw error;
        }
    },
    getLeads: async (): Promise<Lead[]> => {
        try {
            const response = await axios.get(`${API_URL}/leads`);
            return response.data;
        } catch (error) {
            console.error("Error fetching leads:", error);
            throw error;
        }
    },
};
