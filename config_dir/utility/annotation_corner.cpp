#include <opencv2/opencv.hpp>
#include <iostream>
#include <sstream>

using namespace std;
using namespace cv;

typedef vector<Point> Points;
Points getCorners;

static void onMouse(int event, int x, int y, int flags, void* userdata){
	if(event == EVENT_LBUTTONDOWN){
		getCorners.emplace_back(Point(x,y));
	}
	if(event == EVENT_RBUTTONDOWN){
		getCorners.erase(getCorners.end());
	}
}

int main(int argc, char** argv){
	const String keys= "{name_img | | name of image to be annotated}"
						"{name_yaml | | name of yaml file to store annotated data}";

	CommandLineParser parser(argc, argv, keys);

	string name_foto = parser.get<string>("name_img");
	cout << "name_foto: " << name_foto << endl;

	Mat foto_peta = imread(name_foto);
	string name_yaml =  parser.get<string>("name_yaml");

	vector<Mat> MatBuffer;
	FileStorage fsBuffer(name_yaml, FileStorage::READ);

	int wilayah;
	fsBuffer["nwilayah"] >> wilayah;
	MatBuffer.resize(wilayah);

	for(int k=0; k<wilayah; k++){
		stringstream ssk;
		ssk << k;
		fsBuffer["Corner_" + ssk.str()] >> MatBuffer[k];
	}

	fsBuffer.release();

	namedWindow(name_foto, CV_WINDOW_NORMAL);
	setMouseCallback(name_foto, onMouse, 0);

	while(true){
		Mat foto_peta_clone = foto_peta.clone();
		for(int s=0; s< getCorners.size(); s++)
			circle(foto_peta_clone, getCorners[s], 2, Scalar(255,0,0), -1);
		imshow(name_foto, foto_peta_clone);

		int key_ = waitKey(1);
		if(key_ == 27)
			break;
		else if((char)key_ == 's'){			
			Mat matCorner = Mat(getCorners.size(),2,CV_32S,getCorners.data());
			MatBuffer.emplace_back(matCorner);

			FileStorage fs(name_yaml, FileStorage::WRITE);
			for(int q=0; q<MatBuffer.size(); q++){
				stringstream ss;
				ss << q;
				fs << "Corner_" + ss.str() << MatBuffer[q];
			}
			fs << "nwilayah" << (int)MatBuffer.size();
			fs.release();

			getCorners.clear();
		}
	}

	Mat putih(foto_peta.size(), CV_8UC3, Scalar::all(255));

	FileStorage fsload(name_yaml, FileStorage::READ);
	for(int l=0; l<MatBuffer.size(); l++){
		Mat korner;

		stringstream ssn;
		ssn << l;

		fsload["Corner_" + ssn.str()] >> korner;

		cout << "Corner_" << ssn.str() << ": \t";
		for(int r=0; r< korner.rows; r++){
			circle(putih, Point(korner.at<int>(r,0), korner.at<int>(r,1)), 2, Scalar(50*l,255 - 30*l,40*l), -1);
			cout << Point(korner.at<int>(r,0), korner.at<int>(r,1)) << ", ";
		}
		cout << endl << endl;
	}

	cout << "finish " << endl;
	imshow("putih", putih);
	waitKey(0);
}
