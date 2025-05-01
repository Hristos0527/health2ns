import Foundation

struct NightscoutConfig {
    let url: URL
    let apiSecret: String

    static let urlKey = "nightscout_url"
    static let apiKey = "nightscout_api"

    static func save(urlString: String, apiSecret: String) {
        UserDefaults.standard.set(urlString, forKey: urlKey)
        UserDefaults.standard.set(apiSecret, forKey: apiKey)
    }

    static func load() -> NightscoutConfig? {
        guard
            let urlString = UserDefaults.standard.string(forKey: urlKey),
            let url = URL(string: urlString),
            let api = UserDefaults.standard.string(forKey: apiKey)
        else {
            return nil
        }
        return NightscoutConfig(url: url, apiSecret: api)
    }
}
