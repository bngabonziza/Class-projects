package edu.asu.cse535.group14.ecgproject;

import android.util.Log;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

import Forecast.insights.timeseries.arima.Arima;
import Forecast.insights.timeseries.arima.struct.ArimaParams;
import Forecast.insights.timeseries.arima.struct.ForecastResult;

public class ECG implements java.io.Serializable
{
    public double Time;
    public double Signal;
    public double SmoothSignal;
    public boolean Peak;

    public static ArrayList<ECG> GetSubList(int StartTime, int Minutes)
    {
        ArrayList<ECG> Data;
        List<ECG> SubList;
        SubList = Common.AllData.subList(StartTime * 60 * 250 + 1 - Common.Lag, (StartTime + Minutes) * 60 * 250 + 1 + Common.Lag);
        Data = new ArrayList<ECG>(SubList);
        return  Data;
    }

    public static ArrayList<ECG> GetFinalData() throws Exception
    {
        ArrayList<ECG> Data = new ArrayList<ECG>();
        ECG E;
        int index = 0;

        BufferedReader br = null;
        String line = "";

        try
        {
            br = new BufferedReader(new FileReader(Common.CSV_FILE));

            //skip first line
            line = br.readLine();

            while ((line = br.readLine()) != null)
            {
                // use comma as separator
                String[] Values = line.split("\t");

                //if (!IsFloat(Values[0])) continue;

                E = new ECG();
                E.Time = Float.parseFloat(Values[0]);
                E.Signal = Float.parseFloat(Values[1]);
                E.SmoothSignal = Float.parseFloat(Values[2]);
                E.Peak = Values[3].equals("true");

                Data.add(E);
                index++;
            }

        }
        catch (Exception e)
        {
            Log.e("CSE535", "exception", e);
        }
        finally
        {
            if (br != null) br.close();
        }

        return Data;
    }


    public static ArrayList<ECG> GetAllData() throws Exception
    {
        ArrayList<ECG> Data = new ArrayList<ECG>();
        ECG E;
        int index = 0;

        BufferedReader br = null;
        String line = "";

        try
        {
            br = new BufferedReader(new FileReader(Common.CSV_FILE));

            //skip first line
            line = br.readLine();

            while ((line = br.readLine()) != null)
            {
                // use comma as separator
                String[] Values = line.split(",");

                //if (!IsFloat(Values[0])) continue;

                E = new ECG();
                E.Time = Float.parseFloat(Values[0]);
                E.Signal = Float.parseFloat(Values[1]);

                E.Peak = false;

                Data.add(E);
                index++;
            }

        }
        catch (Exception e)
        {
            Log.e("CSE535", "exception", e);
        }
        finally
        {
            if (br != null) br.close();
        }

        return Data;
    }

    public static boolean IsFloat(String Str)
    {
        try
        {
            Float.parseFloat(Str);
            return true;
        } catch (Exception e)
        {
            return false;
        }
    }

    public static ArrayList<ECG> CompressPeaks(ArrayList<ECG> Data)
    {
        boolean PeakStarted = false;
        ECG E;

        //QRS signal lasts for arounf 100ms or 25 samples.
        //Therefore is a peak is deteced then the next 12 samples should not be a peak

        for (int i = 0 + Common.Lag; i < Data.size()-Common.Lag; i++)
        {
            E = Data.get(i);

            if ((PeakStarted == false) && (!E.Peak))
            {
                continue;
            }

            if ((PeakStarted == false) && (E.Peak))
            {
                PeakStarted = true;
                continue;
            }

            if ((PeakStarted == true) && (!E.Peak))
            {
                PeakStarted = false;
                continue;
            }

            if ((PeakStarted == true) && (E.Peak))
            {
                E.Peak = false;
                continue;
            }

        }

        return Data;
    }

    public static ArrayList<ECG> DeclusterPeaks(ArrayList<ECG> Data)
    {
        ECG E;

        //QRS signal lasts for around 100ms or 25 samples.
        //Therefore if a peak is deteced then the next 10 samples should not be a peak
        int Buf = 30;

        for (int i = 0 + Common.Lag; i < Data.size()-Common.Lag; i++)
        {
            E = Data.get(i);

            if (E.Peak)
            {
                //Remove peaks in 30 samples before and after but preserve  the
                //original peak
                for (int j = i-Buf; j <= i+Buf; j++)
                {
                    if (j < 0) continue;
                    if (j >= Data.size()) continue;

                    Data.get(j).Peak = false;
                }

                //Restore the original peak;
                E.Peak = true;
            }
        }

        return Data;
    }

    public static ArrayList<ECG> DetectPeaks(ArrayList<ECG> Data)
    {
        //ArrayList<ECG> Peaks = new ArrayList<ECG>();
        double[] Y = new double[Data.size()];
        double[] FilteredY = new double[Data.size()];


        for (int i = 0; i < Data.size(); i++)
        {
            FilteredY[i] = 0.0;

            Data.get(i).Peak = false;

            Y[i] = Data.get(i).Signal;

            if (i < Common.Lag)
                FilteredY[i] = Data.get(i).Signal;
        }

        double avgFilter[] = new double[Data.size()];
        double stdFilter[] = new double[Data.size()];
        double avg;

        avg = GetAverage(Y, 0, Common.Lag-1);
        avgFilter[Common.Lag-1] = avg;
        stdFilter[Common.Lag-1] = GetStdDev(Y, 0, Common.Lag-1, avg);


        for (int i = Common.Lag; i < Data.size(); i++)
        {
            if (Math.abs(Y[i] - avgFilter[i-1]) > Common.StdDevThreshold*stdFilter[i-1])
            {
                if (Y[i] < avgFilter[i-1])
                    Data.get(i).Peak = true;

                FilteredY[i] =  Common.PeakInfluence*Y[i] + (1-Common.PeakInfluence)*FilteredY[i-1];
            }
            else
            {
                Data.get(i).Peak = false;
                FilteredY[i] =  Y[i];
            }

            avg = GetAverage(FilteredY, (i-Common.Lag), i);
            avgFilter[i] = avg;
            stdFilter[i] = GetStdDev(FilteredY, (i-Common.Lag), i, avg);
        }

        return Data;
    }

    public static double GetAverage(double Y[], int start, int end)
    {
        double sum = 0.0;
        double count = (end-start+1);

        sum = 0.0;
        for (int i = start; i <= end; i++)
        {
            if (i >= Y.length) break;
            sum = sum + Y[i];
        }

        return sum / count;
    }

    public static double GetStdDev(double Y[], int start, int end, double mean)
    {
        double std = 0.0;
        double count = (end-start+1);

        for (int i = start; i <= end; i++)
        {
            if (i >= Y.length) break;
            std = std + Math.pow(Y[i] - mean, 2);
        }

        return Math.sqrt(std/count);
    }

    public static ArrayList<ECG> SmoothNoise(ArrayList<ECG> Data)
    {
        try
        {
            ArrayList<Double> X = new ArrayList<Double>();
            ArrayList<Double> Y = null;

            for (int i=0; i < Data.size(); i++)
            {
                X.add(Data.get(i).Signal);
            }

            KalmanFilter Kalman = new KalmanFilter(X);

            Y = Kalman.calc();

            Data.get(0).SmoothSignal = 0;
            for (int i=1; i < Data.size(); i++)
            {
                Data.get(i).SmoothSignal = Y.get(i-1);
            }

            return Data;
        }
        catch (Exception e)
        {
            Log.e("CSE535", "exception", e);
        }

        return null;
    }

    public static ArrayList<Integer> PredictHeartRate(ArrayList<Integer> HR, int ForecastSize, int ForecastLag)
    {
        ArrayList<Integer> Forecast = new ArrayList<Integer>();
        double[] Data = new double[ForecastLag];

        // Set ARIMA model parameters.
        // Autoregressive Integrated Moving Average
        int p = 2;
        int d = 1;
        int q = 2;
        int P = 0;
        int D = 0;
        int Q = 0;
        int m = 0;


        int k = 0;
        for (int i = (HR.size() - ForecastLag); i < HR.size(); i++)
        {
            Data[k++] = (double)HR.get(i);
        }

        ArimaParams params = new ArimaParams(p, d, q, P, D, Q, m);

        Arima.forecast_arima(Data, ForecastSize, params);
        // Obtain forecast result. The structure contains forecasted values and performance metric etc.
        ForecastResult forecastResult = Arima.forecast_arima(Data, ForecastSize, params);

        // Read forecast values
        double[] forecastData = forecastResult.getForecast();

        // You can obtain upper- and lower-bounds of confidence intervals on forecast values.
        // By default, it computes at 95%-confidence level. This value can be adjusted in ForecastUtil.java
        double[] uppers = forecastResult.getForecastUpperConf();
        double[] lowers = forecastResult.getForecastLowerConf();

        // You can also obtain the root mean-square error as validation metric.
        double rmse = forecastResult.getRMSE();

        // It also provides the maximum normalized variance of the forecast values and their confidence interval.
        double maxNormalizedVariance = forecastResult.getMaxNormalizedVariance();

        // Finally you can read log messages.
        String log = forecastResult.getLog();


        for (int i = 0; i < forecastData.length; i++)
        {
            Forecast.add((int)forecastData[i]);
        }

        return Forecast;
    }

    public static ArrayList<Integer> PredictHeartRate(ArrayList<Integer> HR, int ForecastSize)
    {
        ArrayList<Integer> Forecast = new ArrayList<Integer>();
        double[] Data = new double[HR.size()];

        // Set ARIMA model parameters.
        // Autoregressive Integrated Moving Average
        int p = 1;
        int d = 1;
        int q = 2;
        int P = 0;
        int D = 0;
        int Q = 0;
        int m = 0;


        for (int i= 0; i < HR.size(); i++)
        {
            Data[i] = (double)HR.get(i);
        }

        ArimaParams params = new ArimaParams(p, d, q, P, D, Q, m);

        Arima.forecast_arima(Data, ForecastSize, params);
        // Obtain forecast result. The structure contains forecasted values and performance metric etc.
        ForecastResult forecastResult = Arima.forecast_arima(Data, ForecastSize, params);

        // Read forecast values
        double[] forecastData = forecastResult.getForecast();

        // You can obtain upper- and lower-bounds of confidence intervals on forecast values.
        // By default, it computes at 95%-confidence level. This value can be adjusted in ForecastUtil.java
        double[] uppers = forecastResult.getForecastUpperConf();
        double[] lowers = forecastResult.getForecastLowerConf();

        // You can also obtain the root mean-square error as validation metric.
        double rmse = forecastResult.getRMSE();

        // It also provides the maximum normalized variance of the forecast values and their confidence interval.
        double maxNormalizedVariance = forecastResult.getMaxNormalizedVariance();

        // Finally you can read log messages.
        String log = forecastResult.getLog();


        for (int i = 0; i < forecastData.length; i++)
        {
            Forecast.add((int)forecastData[i]);
        }

        return Forecast;
    }


    public static ArrayList<Integer> GetHeartRate(ArrayList<ECG> Data, int Seconds)
    {
        ArrayList<Integer> HR = new ArrayList<Integer>();
        int PeakCount = 0;

        int Samples = Seconds * 250;
        int Groups = Data.size() / Samples;
        int Start, End;

        for (int G = 1; G <= Groups + 1; G++)
        {
            PeakCount = 0;
            Start = (G-1)*Samples;
            End = Start + Samples;

            for (int i = Start; i < End; i++)
            {
                if (i >= Data.size()) break;

                ECG E = Data.get(i);
                if (E.Peak) PeakCount++;
            }

            //In the first group the lag need to be taken into account
            if (G == 1)
            {
                PeakCount = Samples * (PeakCount) / (Samples-Common.Lag);
            }

            //HR.add(PeakCount);

            if ((PeakCount < 180) && (PeakCount > 50))
            {
                HR.add(PeakCount);
            }
        }

        return HR;
    }
}
