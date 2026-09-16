import Foundation

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case serverError(Int, String)
    case unauthorized
}

extension APIError: LocalizedError {
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "请求地址无效"
        case .networkError(let error):
            return "网络错误：\(error.localizedDescription)"
        case .invalidResponse:
            return "服务器响应异常"
        case .serverError(_, let message):
            return message
        case .unauthorized:
            return "登录已过期，请重新登录"
        }
    }
}

class APIClient {
    static let shared = APIClient()
    private let baseURL = URL(string: "http://localhost:8000/api/v1/")!

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

    private enum CodingKeys: String, CodingKey {
        case code, message, data
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        code = try container.decode(Int.self, forKey: .code)
        message = try container.decode(String.self, forKey: .message)
        if T.self == EmptyResponse.self {
            data = (try container.decodeIfPresent(T.self, forKey: .data)) ?? EmptyResponse() as! T
        } else {
            data = try container.decode(T.self, forKey: .data)
        }
    }
}

/// Used for endpoints whose success response has `"data": null`.
struct EmptyResponse: Decodable {}
