import Foundation
import HealthKit

class HealthKitManager: ObservableObject {
    static let shared = HealthKitManager()
    private let healthStore = HKHealthStore()
    private let glucoseType = HKQuantityType.quantityType(forIdentifier: .bloodGlucose)!
    private var lastSentTimestamp: Date?

    @Published var lastUpdateMessage: String = "Még nem küldtünk adatot."

    init() {
        requestAuthorization()
    }

    func requestAuthorization() {
        let typesToRead: Set = [glucoseType]
        healthStore.requestAuthorization(toShare: nil, read: typesToRead) { success, error in
            if success {
                self.enableBackgroundDelivery()
                self.startObserverQuery()
            } else {
                print("HealthKit engedély hiba: \(error?.localizedDescription ?? "ismeretlen")")
            }
        }
    }

    private func enableBackgroundDelivery() {
        healthStore.enableBackgroundDelivery(for: glucoseType, frequency: .immediate) { success, error in
            if success {
                print("Háttérfrissítés engedélyezve.")
            } else {
                print("Nem sikerült engedélyezni háttérfrissítést: \(error?.localizedDescription ?? "ismeretlen hiba")")
            }
        }
    }

    private func startObserverQuery() {
        let query = HKObserverQuery(sampleType: glucoseType, predicate: nil) { [weak self] _, completionHandler, error in
            if let error = error {
                print("ObserverQuery hiba: \(error.localizedDescription)")
                return
            }
            self?.fetchLatestGlucoseValue()
            completionHandler()
        }
        healthStore.execute(query)
    }

    private func fetchLatestGlucoseValue() {
        let sort = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        let query = HKSampleQuery(sampleType: glucoseType,
                                  predicate: nil,
                                  limit: 1,
                                  sortDescriptors: [sort]) { [weak self] _, samples, error in
            guard let sample = samples?.first as? HKQuantitySample else {
                print("Nincs új minta.")
                return
            }
            let mgdl = Int(sample.quantity.doubleValue(for: .init(from: "mg/dL")))
            let timestamp = sample.startDate
            self?.sendToNightscout(value: mgdl, timestamp: timestamp)
        }
        healthStore.execute(query)
    }

    private func sendToNightscout(value: Int, timestamp: Date) {
        guard let config = NightscoutConfig.load() else {
            print("Nincs beállítva a Nightscout konfiguráció.")
            return
        }

        let entry: [String: Any] = [
            "type": "sgv",
            "sgv": value,
            "date": Int(timestamp.timeIntervalSince1970 * 1000),
            "dateString": ISO8601DateFormatter().string(from: timestamp),
            "device": "ios.healthkit.auto"
        ]

        var request = URLRequest(url: config.url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(config.apiSecret, forHTTPHeaderField: "api-secret")

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: [entry], options: [])
        } catch {
            print("JSON hiba: \(error)")
            return
        }

        URLSession.shared.dataTask(with: request) { [weak self] _, response, error in
            if let error = error {
                print("Hálózati hiba: \(error.localizedDescription)")
                return
            }
            DispatchQueue.main.async {
                self?.lastSentTimestamp = timestamp
                self?.lastUpdateMessage = "Utolsó küldés: \(timestamp.formatted()) – \(value) mg/dL"
                print("Sikeres adatküldés.")
            }
        }.resume()
    }
}
