// vnctpmd.cpp : ���� DLL Ӧ�ó���ĵ���������
//

#include "vnctpmd.h"


///-------------------------------------------------------------------------------------
///C++�Ļص����������ݱ��浽������
///-------------------------------------------------------------------------------------

void MdApi::OnFrontConnected()
{
	Task task = Task();
	task.task_name = ONFRONTCONNECTED;
	this->task_queue.push(task);
};

void MdApi::OnFrontDisconnected(int nReason)
{
	Task task = Task();
	task.task_name = ONFRONTDISCONNECTED;
	task.task_id = nReason;
	this->task_queue.push(task);
};

void MdApi::OnHeartBeatWarning(int nTimeLapse)
{
	Task task = Task();
	task.task_name = ONHEARTBEATWARNING;
	task.task_id = nTimeLapse;
	this->task_queue.push(task);
};

void MdApi::OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUSERLOGIN;
	if (pRspUserLogin)
	{
		CThostFtdcRspUserLoginField *task_data = new CThostFtdcRspUserLoginField();
		*task_data = *pRspUserLogin;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUserLogout(CThostFtdcUserLogoutField *pUserLogout, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUSERLOGOUT;
	if (pUserLogout)
	{
		CThostFtdcUserLogoutField *task_data = new CThostFtdcUserLogoutField();
		*task_data = *pUserLogout;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPERROR;
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPSUBMARKETDATA;
	if (pSpecificInstrument)
	{
		CThostFtdcSpecificInstrumentField *task_data = new CThostFtdcSpecificInstrumentField();
		*task_data = *pSpecificInstrument;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUNSUBMARKETDATA;
	if (pSpecificInstrument)
	{
		CThostFtdcSpecificInstrumentField *task_data = new CThostFtdcSpecificInstrumentField();
		*task_data = *pSpecificInstrument;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPSUBFORQUOTERSP;
	if (pSpecificInstrument)
	{
		CThostFtdcSpecificInstrumentField *task_data = new CThostFtdcSpecificInstrumentField();
		*task_data = *pSpecificInstrument;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUNSUBFORQUOTERSP;
	if (pSpecificInstrument)
	{
		CThostFtdcSpecificInstrumentField *task_data = new CThostFtdcSpecificInstrumentField();
		*task_data = *pSpecificInstrument;
		task.task_data = task_data;
	}
	if (pRspInfo)
	{
		CThostFtdcRspInfoField *task_error = new CThostFtdcRspInfoField();
		*task_error = *pRspInfo;
		task.task_error = task_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *pDepthMarketData)
{
	Task task = Task();
	task.task_name = ONRTNDEPTHMARKETDATA;
	if (pDepthMarketData)
	{
		CThostFtdcDepthMarketDataField *task_data = new CThostFtdcDepthMarketDataField();
		*task_data = *pDepthMarketData;
		task.task_data = task_data;
	}
	this->task_queue.push(task);
};

void MdApi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField *pForQuoteRsp)
{
	Task task = Task();
	task.task_name = ONRTNFORQUOTERSP;
	if (pForQuoteRsp)
	{
		CThostFtdcForQuoteRspField *task_data = new CThostFtdcForQuoteRspField();
		*task_data = *pForQuoteRsp;
		task.task_data = task_data;
	}
	this->task_queue.push(task);
};




///-------------------------------------------------------------------------------------
///�����̴߳Ӷ�����ȡ�����ݣ�ת��Ϊpython����󣬽�������
///-------------------------------------------------------------------------------------

void MdApi::processTask()
{
	while (this->active)
	{
		Task task = this->task_queue.pop();
		
		switch (task.task_name)
		{
		case ONFRONTCONNECTED:
		{
			this->processFrontConnected(&task);
			break;
		}

		case ONFRONTDISCONNECTED:
		{
			this->processFrontDisconnected(&task);
			break;
		}

		case ONHEARTBEATWARNING:
		{
			this->processHeartBeatWarning(&task);
			break;
		}

		case ONRSPUSERLOGIN:
		{
			this->processRspUserLogin(&task);
			break;
		}

		case ONRSPUSERLOGOUT:
		{
			this->processRspUserLogout(&task);
			break;
		}

		case ONRSPERROR:
		{
			this->processRspError(&task);
			break;
		}

		case ONRSPSUBMARKETDATA:
		{
			this->processRspSubMarketData(&task);
			break;
		}

		case ONRSPUNSUBMARKETDATA:
		{
			this->processRspUnSubMarketData(&task);
			break;
		}

		case ONRSPSUBFORQUOTERSP:
		{
			this->processRspSubForQuoteRsp(&task);
			break;
		}

		case ONRSPUNSUBFORQUOTERSP:
		{
			this->processRspUnSubForQuoteRsp(&task);
			break;
		}

		case ONRTNDEPTHMARKETDATA:
		{
			this->processRtnDepthMarketData(&task);
			break;
		}

		case ONRTNFORQUOTERSP:
		{
			this->processRtnForQuoteRsp(&task);
			break;
		}
		};
	}
};

void MdApi::processFrontConnected(Task *task)
{
	gil_scoped_acquire acquire;
	this->onFrontConnected();
};

void MdApi::processFrontDisconnected(Task *task)
{
	gil_scoped_acquire acquire;
	this->onFrontDisconnected(task->task_id);
};

void MdApi::processHeartBeatWarning(Task *task)
{
	gil_scoped_acquire acquire;
	this->onHeartBeatWarning(task->task_id);
};

void MdApi::processRspUserLogin(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcRspUserLoginField *task_data = (CThostFtdcRspUserLoginField*)task->task_data;
		data["TradingDay"] = task_data->TradingDay;
		data["LoginTime"] = task_data->LoginTime;
		data["BrokerID"] = task_data->BrokerID;
		data["UserID"] = task_data->UserID;
		data["SystemName"] = task_data->SystemName;
		data["FrontID"] = task_data->FrontID;
		data["SessionID"] = task_data->SessionID;
		data["MaxOrderRef"] = task_data->MaxOrderRef;
		data["SHFETime"] = task_data->SHFETime;
		data["DCETime"] = task_data->DCETime;
		data["CZCETime"] = task_data->CZCETime;
		data["FFEXTime"] = task_data->FFEXTime;
		data["INETime"] = task_data->INETime;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspUserLogin(data, error, task->task_id, task->task_last);
};

void MdApi::processRspUserLogout(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcUserLogoutField *task_data = (CThostFtdcUserLogoutField*)task->task_data;
		data["BrokerID"] = task_data->BrokerID;
		data["UserID"] = task_data->UserID;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspUserLogout(data, error, task->task_id, task->task_last);
};

void MdApi::processRspError(Task *task)
{
	gil_scoped_acquire acquire;
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspError(error, task->task_id, task->task_last);
};

void MdApi::processRspSubMarketData(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcSpecificInstrumentField *task_data = (CThostFtdcSpecificInstrumentField*)task->task_data;
		data["InstrumentID"] = task_data->InstrumentID;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspSubMarketData(data, error, task->task_id, task->task_last);
};

void MdApi::processRspUnSubMarketData(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcSpecificInstrumentField *task_data = (CThostFtdcSpecificInstrumentField*)task->task_data;
		data["InstrumentID"] = task_data->InstrumentID;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspUnSubMarketData(data, error, task->task_id, task->task_last);
};

void MdApi::processRspSubForQuoteRsp(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcSpecificInstrumentField *task_data = (CThostFtdcSpecificInstrumentField*)task->task_data;
		data["InstrumentID"] = task_data->InstrumentID;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspSubForQuoteRsp(data, error, task->task_id, task->task_last);
};

void MdApi::processRspUnSubForQuoteRsp(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcSpecificInstrumentField *task_data = (CThostFtdcSpecificInstrumentField*)task->task_data;
		data["InstrumentID"] = task_data->InstrumentID;
		delete task->task_data;
	}
	dict error;
	if (task->task_error)
	{
		CThostFtdcRspInfoField *task_error = (CThostFtdcRspInfoField*)task->task_error;
		error["ErrorID"] = task_error->ErrorID;
		error["ErrorMsg"] = task_error->ErrorMsg;
		delete task->task_error;
	}
	this->onRspUnSubForQuoteRsp(data, error, task->task_id, task->task_last);
};

void MdApi::processRtnDepthMarketData(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcDepthMarketDataField *task_data = (CThostFtdcDepthMarketDataField*)task->task_data;
		data["TradingDay"] = task_data->TradingDay;
		data["InstrumentID"] = task_data->InstrumentID;
		data["ExchangeID"] = task_data->ExchangeID;
		data["ExchangeInstID"] = task_data->ExchangeInstID;
		data["LastPrice"] = task_data->LastPrice;
		data["PreSettlementPrice"] = task_data->PreSettlementPrice;
		data["PreClosePrice"] = task_data->PreClosePrice;
		data["PreOpenInterest"] = task_data->PreOpenInterest;
		data["OpenPrice"] = task_data->OpenPrice;
		data["HighestPrice"] = task_data->HighestPrice;
		data["LowestPrice"] = task_data->LowestPrice;
		data["Volume"] = task_data->Volume;
		data["Turnover"] = task_data->Turnover;
		data["OpenInterest"] = task_data->OpenInterest;
		data["ClosePrice"] = task_data->ClosePrice;
		data["SettlementPrice"] = task_data->SettlementPrice;
		data["UpperLimitPrice"] = task_data->UpperLimitPrice;
		data["LowerLimitPrice"] = task_data->LowerLimitPrice;
		data["PreDelta"] = task_data->PreDelta;
		data["CurrDelta"] = task_data->CurrDelta;
		data["UpdateTime"] = task_data->UpdateTime;
		data["UpdateMillisec"] = task_data->UpdateMillisec;
		data["BidPrice1"] = task_data->BidPrice1;
		data["BidVolume1"] = task_data->BidVolume1;
		data["AskPrice1"] = task_data->AskPrice1;
		data["AskVolume1"] = task_data->AskVolume1;
		data["BidPrice2"] = task_data->BidPrice2;
		data["BidVolume2"] = task_data->BidVolume2;
		data["AskPrice2"] = task_data->AskPrice2;
		data["AskVolume2"] = task_data->AskVolume2;
		data["BidPrice3"] = task_data->BidPrice3;
		data["BidVolume3"] = task_data->BidVolume3;
		data["AskPrice3"] = task_data->AskPrice3;
		data["AskVolume3"] = task_data->AskVolume3;
		data["BidPrice4"] = task_data->BidPrice4;
		data["BidVolume4"] = task_data->BidVolume4;
		data["AskPrice4"] = task_data->AskPrice4;
		data["AskVolume4"] = task_data->AskVolume4;
		data["BidPrice5"] = task_data->BidPrice5;
		data["BidVolume5"] = task_data->BidVolume5;
		data["AskPrice5"] = task_data->AskPrice5;
		data["AskVolume5"] = task_data->AskVolume5;
		data["AveragePrice"] = task_data->AveragePrice;
		data["ActionDay"] = task_data->ActionDay;
		delete task->task_data;
	}
	this->onRtnDepthMarketData(data);
};

void MdApi::processRtnForQuoteRsp(Task *task)
{
	gil_scoped_acquire acquire;
	dict data;
	if (task->task_data)
	{
		CThostFtdcForQuoteRspField *task_data = (CThostFtdcForQuoteRspField*)task->task_data;
		data["TradingDay"] = task_data->TradingDay;
		data["InstrumentID"] = task_data->InstrumentID;
		data["ForQuoteSysID"] = task_data->ForQuoteSysID;
		data["ForQuoteTime"] = task_data->ForQuoteTime;
		data["ActionDay"] = task_data->ActionDay;
		data["ExchangeID"] = task_data->ExchangeID;
		delete task->task_data;
	}
	this->onRtnForQuoteRsp(data);
};


///-------------------------------------------------------------------------------------
///��������
///-------------------------------------------------------------------------------------

void MdApi::createFtdcMdApi(string pszFlowPath)
{
	this->api = CThostFtdcMdApi::CreateFtdcMdApi(pszFlowPath.c_str());
	this->api->RegisterSpi(this);
};

void MdApi::release()
{
	this->api->Release();
};

void MdApi::init()
{
	this->active = true;
	this->task_thread = thread(&MdApi::processTask, this);

	this->api->Init();
};

int MdApi::join()
{
	int i = this->api->Join();
	return i;
};

int MdApi::exit()
{
	//�ú�����ԭ��API��û�У����ڰ�ȫ�˳�API�ã�ԭ����join�ƺ���̫�ȶ�
	this->api->RegisterSpi(NULL);
	this->api->Release();
	this->api = NULL;
	return 1;
};

string MdApi::getTradingDay()
{
	string day = this->api->GetTradingDay();
	return day;
};

void MdApi::registerFront(string pszFrontAddress)
{
	this->api->RegisterFront((char*)pszFrontAddress.c_str());
};

int MdApi::subscribeMarketData(string instrumentID)
{
	char* buffer = (char*) instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::unSubscribeMarketData(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };;
	int i = this->api->UnSubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::subscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::unSubscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };;
	int i = this->api->UnSubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::reqUserLogin(dict req, int reqid)
{
	CThostFtdcReqUserLoginField myreq = CThostFtdcReqUserLoginField();
	memset(&myreq, 0, sizeof(myreq));
	getString(req, "TradingDay", myreq.TradingDay);
	getString(req, "BrokerID", myreq.BrokerID);
	getString(req, "UserID", myreq.UserID);
	getString(req, "Password", myreq.Password);
	getString(req, "UserProductInfo", myreq.UserProductInfo);
	getString(req, "InterfaceProductInfo", myreq.InterfaceProductInfo);
	getString(req, "ProtocolInfo", myreq.ProtocolInfo);
	getString(req, "MacAddress", myreq.MacAddress);
	getString(req, "OneTimePassword", myreq.OneTimePassword);
	getString(req, "ClientIPAddress", myreq.ClientIPAddress);
	getString(req, "LoginRemark", myreq.LoginRemark);
	getInt(req, "ClientIPPort", &myreq.ClientIPPort);
	int i = this->api->ReqUserLogin(&myreq, reqid);
	return i;
};

int MdApi::reqUserLogout(dict req, int reqid)
{
	CThostFtdcUserLogoutField myreq = CThostFtdcUserLogoutField();
	memset(&myreq, 0, sizeof(myreq));
	getString(req, "BrokerID", myreq.BrokerID);
	getString(req, "UserID", myreq.UserID);
	int i = this->api->ReqUserLogout(&myreq, reqid);
	return i;
};


///-------------------------------------------------------------------------------------
///Boost.Python��װ
///-------------------------------------------------------------------------------------

class PyMdApi: public MdApi
{
public:
	using MdApi::MdApi;

	void onFrontConnected() override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onFrontConnected);
	};

	void onFrontDisconnected(int reqid) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onFrontDisconnected, reqid);
	};

	void onHeartBeatWarning(int reqid) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onHeartBeatWarning, reqid);
	};

	void onRspUserLogin(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspUserLogin, data, error, reqid, last);
	};

	void onRspUserLogout(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspUserLogout, data, error, reqid, last);
	};

	void onRspError(dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspError, error, reqid, last);
	};

	void onRspSubMarketData(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspSubMarketData, data, error, reqid, last);
	};

	void onRspUnSubMarketData(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspUnSubMarketData, data, error, reqid, last);
	};

	void onRspSubForQuoteRsp(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspSubForQuoteRsp, data, error, reqid, last);
	};

	void onRspUnSubForQuoteRsp(dict data, dict error, int reqid, bool last) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRspUnSubForQuoteRsp, data, error, reqid, last);
	};

	void onRtnDepthMarketData(dict data) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRtnDepthMarketData, data);
	};

	void onRtnForQuoteRsp(dict data) override
	{
		PYBIND11_OVERLOAD_PURE(void, MdApi, onRtnForQuoteRsp, data);
	};
};


PYBIND11_MODULE(vnctpmd, m)
{
	PyEval_InitThreads();	//����ʱ���У���֤�ȴ���GIL

	class_<MdApi, PyMdApi> mdapi(m, "MdApi");
	mdapi
		.def(init<>())
		.def("createFtdcMdApi", &MdApi::createFtdcMdApi)
		.def("release", &MdApi::release)
		.def("init", &MdApi::init)
		.def("join", &MdApi::join)
		.def("exit", &MdApi::exit)
		.def("getTradingDay", &MdApi::getTradingDay)
		.def("registerFront", &MdApi::registerFront)
		.def("subscribeMarketData", &MdApi::subscribeMarketData)
		.def("unSubscribeMarketData", &MdApi::unSubscribeMarketData)
		.def("subscribeForQuoteRsp", &MdApi::subscribeForQuoteRsp)
		.def("unSubscribeForQuoteRsp", &MdApi::unSubscribeForQuoteRsp)
		.def("reqUserLogin", &MdApi::reqUserLogin)
		.def("reqUserLogout", &MdApi::reqUserLogout)

		.def("onFrontConnected", &MdApi::onFrontConnected)
		.def("onFrontDisconnected", &MdApi::onFrontDisconnected)
		.def("onHeartBeatWarning", &MdApi::onHeartBeatWarning)
		.def("onRspUserLogin", &MdApi::onRspUserLogin)
		.def("onRspUserLogout", &MdApi::onRspUserLogout)
		.def("onRspError", &MdApi::onRspError)
		.def("onRspSubMarketData", &MdApi::onRspSubMarketData)
		.def("onRspUnSubMarketData", &MdApi::onRspUnSubMarketData)
		.def("onRspSubForQuoteRsp", &MdApi::onRspSubForQuoteRsp)
		.def("onRspUnSubForQuoteRsp", &MdApi::onRspUnSubForQuoteRsp)
		.def("onRtnDepthMarketData", &MdApi::onRtnDepthMarketData)
		.def("onRtnForQuoteRsp", &MdApi::onRtnForQuoteRsp)
		;
}
