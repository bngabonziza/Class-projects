package edu.asu.cse535.group14.ecgproject;

import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.IntentSender;
import android.content.ServiceConnection;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.content.res.Configuration;
import android.content.res.Resources;
import android.database.DatabaseErrorHandler;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.os.UserHandle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.util.Log;
import android.view.Display;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

public class Common
{
    public static Context Context = null;
    public static String SERVER_URL = "https://www-qa.law.asu.edu/CSE535/ECG/";
    public static String ECG_FILE = "FinalData-Danial.csv"; //"FinalData-Faraz.csv"; //"Faraz-Khan.csv";
    public static String CSV_FILE;
    public static ArrayList<ECG> AllData = null;
    public static ArrayList<ECG> Data = null;
    public static ArrayList<Integer> HR1 = null;
    public static ArrayList<Integer> HR1Pred = null;

    public static double StdDevThreshold = 2.5;
    public static double PeakInfluence = 0.3;
    public static int MinsToLoad = 30;
    public static int Lag = 500;
    public static int ForecastSize = 15; //minutes of projected heart rates
    public static int ForecastLag = 30; //minutes of past heart rates
    public static int BradyCardia = 60;

    public static void ShowMessage(String Msg)
    {
        CharSequence text = Msg;
        int duration = Toast.LENGTH_LONG;

        Toast toast = Toast.makeText(Context, text, duration);
        View view = toast.getView();
        TextView txt = (TextView) view.findViewById(android.R.id.message);

        //view.setBackgroundColor(Color.argb(70,202,124,226));
        view.setBackgroundColor(Color.DKGRAY);
        txt.setTextColor(Color.WHITE);
        txt.setPadding(50, 0, 50, 0);
        toast.show();
    }

    public static void InitCSVFile()
    {
        try
        {
            String DataFolder;

            Boolean IsSDCardPresent = Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED);
            Boolean IsSDCardRemovable = Environment.isExternalStorageRemovable();

            if(IsSDCardRemovable && IsSDCardPresent)
            {
                DataFolder = Environment.getExternalStorageDirectory() + "/Android/Data";
            }
            else
            {
                DataFolder = Context.getExternalFilesDir(null).toString();
            }

            CSV_FILE = DataFolder + "/" + ECG_FILE;

            new File(DataFolder).mkdirs();

        }
        catch (Exception e)
        {
            ShowMessage(e.getMessage());
            Log.e("CSE535", "exception", e);
        }
    }

}
