import Foundation

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case serverError(Int, String)
    case unauthorized
}

class APIClient {
    static let shared = APIClient()
    private let baseURL = URL(string: "http://localhost:8000/api/v1")!

    private init() {}

    func request<T: Decodable>(
        path: String,
        method: String = "GET",
        body: Encodable? = nil,
        token: String? = nil
    ) async throws -> T {
        guard let url = URL(string: path, relativeTo: baseURL) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(httpResponse.statusCode, message)
        }

        let apiResponse = try JSONDecoder().decode(APIResponse<T>.self, from: data)
        return apiResponse.data
    }
}

struct APIResponse<T: Decodable>: Decodable {
    let code: Int
    let message: String
    let data: T
}
