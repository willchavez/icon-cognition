import Foundation
import Vision
import AppKit
let folder = CommandLine.arguments[1]
let files = try FileManager.default.contentsOfDirectory(atPath: folder).filter{$0.hasSuffix(".png")}.sorted()
var output: [String: [[String: Any]]] = [:]
for file in files {
 let url = URL(fileURLWithPath: folder).appendingPathComponent(file)
 let request = VNRecognizeTextRequest()
 request.recognitionLevel = .accurate
 request.usesLanguageCorrection = false
 let handler = VNImageRequestHandler(url: url)
 try handler.perform([request])
 output[file] = (request.results ?? []).map { r in ["text":r.topCandidates(1).first!.string,"confidence":r.topCandidates(1).first!.confidence,"x":r.boundingBox.minX,"y":r.boundingBox.minY,"height":r.boundingBox.height] }
}
let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(data)
