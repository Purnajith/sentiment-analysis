using System;
using System.IO;
using CustomeModel.Data;
using CustomeModel.Data.ScoreMagnitudeVolume;
using Microsoft.ML;

namespace CustomeModel
{
    class Program
    {

        static readonly string basePath = @"C:\Users\purna\source\repos\Purnajith\sentiment-analysis\prediction\price\";
        static readonly string casePath = @"MLNet\Cases\CustomeModel\Data\ScoreMagnitudeVolume";

        static readonly string _trainDataPath = Path.Combine(basePath, "arrangedData-train.csv");
        static readonly string _testDataPath = Path.Combine(basePath, "arrangedData-test.csv");
        static readonly string _modelPath = Path.Combine(basePath, casePath, "Model.zip");

        /*https://docs.microsoft.com/en-us/dotnet/machine-learning/tutorials/predict-prices*/
        static void Main(string[] args)
        {
            MLContext mlContext = new MLContext(seed: 0);
            var model = Train(mlContext, _trainDataPath);

            Evaluate(mlContext, model);

            TestSinglePrediction(mlContext, model);
        }

        public static ITransformer Train(MLContext mlContext, string dataPath)
        {
            IDataView dataView = mlContext.Data.LoadFromTextFile<ModelInput>(dataPath, hasHeader: true, separatorChar: ',');
            var pipeline = mlContext.Transforms.CopyColumns(outputColumnName: "Label", inputColumnName: "volume")
                .Append(mlContext.Transforms.Concatenate("Features", new[] { "companyID", "magnitude", "score" })
                .Append(mlContext.Regression.Trainers.FastTree()));

            var model = pipeline.Fit(dataView);

            return model;
        }

        private static void Evaluate(MLContext mlContext, ITransformer model)
        {
            
            IDataView dataView = mlContext.Data.LoadFromTextFile<ModelInput>(_testDataPath, hasHeader: true, separatorChar: ',');

            var predictions = model.Transform(dataView);

            var metrics = mlContext.Regression.Evaluate(predictions, "Label", "Score");

            Console.WriteLine();
            Console.WriteLine($"*************************************************");
            Console.WriteLine($"*       Model quality metrics evaluation         ");
            Console.WriteLine($"*------------------------------------------------");

            Console.WriteLine($"*       RSquared Score:      {metrics.RSquared:0.##}");

            Console.WriteLine($"*       Root Mean Squared Error:      {metrics.RootMeanSquaredError:#.##}");
        }

        private static void TestSinglePrediction(MLContext mlContext, ITransformer model)
        {
            
            var predictionFunction = mlContext.Model.CreatePredictionEngine<ModelInput, ModelOutput>(model);

            // Create single instance of sample data from first line of dataset for model input
            ModelInput sampleData = new ModelInput()
            {
                CompanyID = 172,
                Magnitude = 0.73F,
                Score = -0.09F,
            };

            // Make a single prediction on the sample data and print results
            var predictionResult = predictionFunction.Predict(sampleData);

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
