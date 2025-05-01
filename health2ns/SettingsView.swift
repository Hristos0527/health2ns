import SwiftUI

struct SettingsView: View {
    @State private var nightscoutUrl: String = UserDefaults.standard.string(forKey: NightscoutConfig.urlKey) ?? ""
    @State private var apiSecret: String = UserDefaults.standard.string(forKey: NightscoutConfig.apiKey) ?? ""
    @State private var message: String?

    var body: some View {
        Form {
            Section(header: Text("Nightscout beállítások")) {
                TextField("URL (https://...)", text: $nightscoutUrl)
                    .autocapitalization(.none)
                    .keyboardType(.URL)

                SecureField("API kulcs", text: $apiSecret)

                Button("Mentés") {
                    if nightscoutUrl.isEmpty || apiSecret.isEmpty {
                        message = "Minden mező kitöltése kötelező!"
                        return
                    }
                    NightscoutConfig.save(urlString: nightscoutUrl, apiSecret: apiSecret)
                    message = "Beállítások elmentve."
                }
            }

            if let message = message {
                Section {
                    Text(message)
                        .foregroundColor(.blue)
                }
            }
        }
        .navigationTitle("Beállítások")
    }
}
