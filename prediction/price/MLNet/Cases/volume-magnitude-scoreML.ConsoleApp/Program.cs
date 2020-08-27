// This file was auto-generated by ML.NET Model Builder. 

using System;
using Volume_magnitude_scoreML.Model;

namespace Volume_magnitude_scoreML.ConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            // Create single instance of sample data from first line of dataset for model input
            ModelInput sampleData = new ModelInput()
            {
                CompanyID = 172F,
                Magnitude = 0.1F,
                Score = -0.1F,
            };

            // Make a single prediction on the sample data and print results
            var predictionResult = ConsumeModel.Predict(sampleData);

            Console.WriteLine("Using model to make single prediction -- Comparing actual Volume with predicted Volume from sample data...\n\n");
            Console.WriteLine($"CompanyID: {sampleData.CompanyID}");
            Console.WriteLine($"Magnitude: {sampleData.Magnitude}");
            Console.WriteLine($"Score: {sampleData.Score}");
            Console.WriteLine($"\n\nPredicted Volume: {predictionResult.Score}\n\n");
            Console.WriteLine("=============== End of process, hit any key to finish ===============");
            Console.ReadKey();
        }
    }
}
