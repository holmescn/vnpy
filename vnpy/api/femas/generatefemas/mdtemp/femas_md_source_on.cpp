void onFrontConnected() override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onFrontConnected);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onFrontDisconnected(int reqid) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onFrontDisconnected, reqid);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onHeartBeatWarning(int reqid) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onHeartBeatWarning, reqid);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onPackageStart(int reqid, int reqid) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onPackageStart, reqid, reqid);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onPackageEnd(int reqid, int reqid) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onPackageEnd, reqid, reqid);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspError(const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspError, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspUserLogin(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspUserLogin, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspUserLogout(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspUserLogout, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRtnDepthMarketData(const dict &data) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRtnDepthMarketData, data);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspSubMarketData(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspSubMarketData, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspUnSubMarketData(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspUnSubMarketData, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspGetMarketTopic(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspGetMarketTopic, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

void onRspGetMarketData(const dict &data, const dict &data, int reqid, bool last) override
{
	try
	{
		PYBIND11_OVERLOAD(void, MdApi, onRspGetMarketData, data, data, reqid, last);
	}
	catch (const error_already_set &e)
	{
		cout << e.what() << endl;
	}
};

