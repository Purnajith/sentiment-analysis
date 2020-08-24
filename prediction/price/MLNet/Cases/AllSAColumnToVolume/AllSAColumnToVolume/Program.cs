﻿using AllSAColumnToVolumeML.Model;
using System;

namespace AllSAColumnToVolume
{
    class Program
    {
        static void Main(string[] args)
        {

            string selection = String.Empty;
            do
            {
                Console.WriteLine("=====================================");

                Console.WriteLine("Please select");
                Console.WriteLine("Build Model = 1");
                Console.WriteLine("Predict = 2");
                Console.WriteLine("Exit = -99");

                selection = Console.ReadLine();

                if (selection == "1")
                {

                }
                else if (selection == "2")
                {
                    Console.WriteLine("Enter - CompanyID");
                    string CompanyID = Console.ReadLine();

                    Console.WriteLine("Enter - Magnitude");
                    string Magnitude = Console.ReadLine();

                    Console.WriteLine("Enter - Polarity");
                    string Polarity = Console.ReadLine();

                    Console.WriteLine("Enter - Score");
                    string Score = Console.ReadLine();

                    Console.WriteLine("Enter - Subjectivity");
                    string Subjectivity = Console.ReadLine();

                    DisplayPredict(Convert.ToInt32(CompanyID),
                                    Convert.ToDouble(Magnitude),
                                    Convert.ToDouble(Polarity),
                                    Convert.ToDouble(Score),
                                    Convert.ToDouble(Subjectivity));

                }

                Console.WriteLine("=====================================");
            }
            while (selection != "-99");
        }

        private static void DisplayPredict(int CompanyID, double Magnitude, double Polarity, double Score, double Subjectivity)
        {
            // Create single instance of sample data from first line of dataset for model input
            ModelInput sampleData = new ModelInput()
            {
                CompanyID = CompanyID,
                Magnitude = (float) Magnitude,
                Polarity = (float) Polarity,
                Score = (float) Score,
                Subjectivity = (float) Subjectivity,
            };

            // Make a single prediction on the sample data and print results
            var predictionResult = ConsumeModel.Predict(sampleData);

            Console.WriteLine("Using model to make single prediction -- Comparing actual Volume with predicted Volume from sample data...\n\n");
            Console.WriteLine($"CompanyID: {sampleData.CompanyID}");
            Console.WriteLine($"Magnitude: {sampleData.Magnitude}");
            Console.WriteLine($"Polarity: {sampleData.Polarity}");
            Console.WriteLine($"Score: {sampleData.Score}");
            Console.WriteLine($"Subjectivity: {sampleData.Subjectivity}");
            Console.WriteLine($"\n\nPredicted Volume: {predictionResult.Score}\n\n");
            Console.WriteLine("=============== End of process, hit any key to finish ===============");
            Console.ReadKey();
        }
    }
}
