using System;
using System.IO;
using CustomeModel.Data;
using CustomeModel.Data.ScoreMagnitudeVolume;
using Microsoft.ML;
using Microsoft.ML.Trainers.FastTree;

namespace CustomeModel
{
    class Program
    {

        static readonly string basePath = @"C:\Users\purna\source\repos\Purnajith\sentiment-analysis\prediction\price\data2\";

        static readonly string _trainDataPathFormat = Path.Combine(basePath, "arrangedData-train.csv");
        static readonly string _testDataPathFormat = Path.Combine(basePath, "arrangedData-test.csv");
        static readonly string _validateDataPathFormat = Path.Combine(basePath, "arrangedData-validate.csv");

        /*https://docs.microsoft.com/en-us/dotnet/machine-learning/tutorials/predict-prices*/
        static void Main(string[] args)
        {
            MLContext mlContextVolume = new MLContext(seed: 0);

            var modelVolume = TrainVolume(mlContextVolume, _trainDataPathFormat);
            Evaluate<ScoreMagnitudeVolume>(mlContextVolume, modelVolume, _validateDataPathFormat);

            string selection = String.Empty;
            do
            {
                Console.WriteLine("Select From Options Below");
                Console.WriteLine("Use Validation Data Set = 1");
                Console.WriteLine("Enter Data = 2");
                Console.WriteLine("Exit = -99");
                selection = Console.ReadLine();

                if (selection == "1")
                {
                    TestValaidateDatePrediction(mlContextVolume,
                                                    modelVolume,
                                                    _testDataPathFormat);
                }
                else if (selection == "2") 
                {
                    TestSinglePrediction(mlContextVolume, modelVolume);
                }

                Console.WriteLine("");
                Console.WriteLine("");
                Console.WriteLine("=============================================================");
            } while (selection != "-99");
        }

        public static ITransformer TrainVolume(MLContext mlContext, string dataPath)
        {
            IDataView dataView = mlContext.Data.LoadFromTextFile<ScoreMagnitudeVolume>(dataPath, hasHeader: true, separatorChar: ',');

            // Data process configuration with pipeline data transformations 
            var pipeline = mlContext.Transforms.CopyColumns(outputColumnName: "Label", inputColumnName: "volume")
                .Append(mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "score" })
                .Append(mlContext.Regression.Trainers.FastTreeTweedie(new FastTreeTweedieTrainer.Options() { NumberOfLeaves = 17, MinimumExampleCountPerLeaf = 1, NumberOfTrees = 100, LearningRate = 0.3504487f, Shrinkage = 0.09932277f, LabelColumnName = "volume", FeatureColumnName = "Features" })));
                //.Append(mlContext.Regression.Trainers.FastForest(numberOfLeaves: 6, minimumExampleCountPerLeaf: 1, numberOfTrees: 500, labelColumnName: "volume", featureColumnName: "Features")));


            var model = pipeline.Fit(dataView);

            return model;
        }

        private static void Evaluate<T>(MLContext mlContext, ITransformer model, string dataPath)
        {
            
            IDataView dataView = mlContext.Data.LoadFromTextFile<T>(dataPath, hasHeader: true, separatorChar: ',');

            var predictions = model.Transform(dataView);

            var metrics = mlContext.Regression.Evaluate(predictions, "Label", "Score");

            Console.WriteLine();
            Console.WriteLine($"*************************************************");
            Console.WriteLine($"*       Model quality metrics evaluation         ");
            Console.WriteLine($"*------------------------------------------------");
            Console.WriteLine($"*       RSquared Score:      {metrics.RSquared:0.##}");
            Console.WriteLine($"*       Root Mean Squared Error:      {metrics.RootMeanSquaredError:#.##}");
        }

        private static void TestSinglePrediction(MLContext mlContextVolume,
                                                   ITransformer modelVolume)
        {
            var predictionFunctionVolume = mlContextVolume.Model.CreatePredictionEngine<ScoreMagnitudeVolume, ModelOutput>(modelVolume);

            float companyID = 0;
            float score = 0;
            float magnitiude = 0;

            Console.WriteLine("companyID:");
            companyID = float.Parse(Console.ReadLine());

            Console.WriteLine("Score:");
            score = float.Parse(Console.ReadLine());

            Console.WriteLine("Magnitiude:");
            magnitiude = float.Parse(Console.ReadLine());

            Console.WriteLine("Using model to make single prediction -- Comparing actual with predicted from sample data...\n\n");
            Console.WriteLine("CompanyID | Magnitude |  Score | Predicted Volume | Actual Volume");

            PredictVolume(predictionFunctionVolume,
                                    companyID,
                                    score,
                                    magnitiude);
        }

        private static void TestValaidateDatePrediction(MLContext mlContextVolume,
                                                   ITransformer modelVolume, 
                                                   string dataPath)
        {
            var predictionFunctionVolume = mlContextVolume.Model.CreatePredictionEngine<ScoreMagnitudeVolume, ModelOutput>(modelVolume);

            Console.WriteLine("Using model to make single prediction -- Comparing actual with predicted from sample data...\n\n");
            Console.WriteLine("CompanyID | Magnitude |  Score | Predicted Volume | Actual Volume");

            using (var reader = new StreamReader(dataPath))
            {
                int count = 0;
                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    var values = line.Split(',');

                    if (count != 0) 
                    {
                        PredictVolume(predictionFunctionVolume,
                                        !String.IsNullOrEmpty(values[1]) ? float.Parse(values[1]) : 0F,
                                        !String.IsNullOrEmpty(values[10]) ? float.Parse(values[10]) : 0F,
                                        !String.IsNullOrEmpty(values[18]) ? float.Parse(values[18]) : 0F,
                                        !String.IsNullOrEmpty(values[20]) ? float.Parse(values[20]) : 0F);
                    }
                    count++;
                }
            }
        }


        public static void PredictVolume(PredictionEngine<ScoreMagnitudeVolume, ModelOutput> predictionFunction, float companyID, float magnitude, float score, float? actualVolume = null)
        {
            // Create single instance of sample data from first line of dataset for model input
            ScoreMagnitudeVolume sampleDataVolume = new ScoreMagnitudeVolume()
            {
                CompanyID = companyID,
                Magnitude = magnitude,
                Score = score,
            };

            // Make a single prediction on the sample data and print results
            var predictionResultVolume = predictionFunction.Predict(sampleDataVolume);

            if (actualVolume.HasValue)
            {
                Console.WriteLine($"{sampleDataVolume.CompanyID} | {sampleDataVolume.Magnitude} | {sampleDataVolume.Score} | {predictionResultVolume.Score} | {actualVolume}");
            }
            else 
            {
                Console.WriteLine($"{sampleDataVolume.CompanyID} | {sampleDataVolume.Magnitude} | {sampleDataVolume.Score} | {predictionResultVolume.Score}");
            }
        }
    }
}
