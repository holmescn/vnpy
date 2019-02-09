//ϵͳ
#ifdef WIN32
#include "stdafx.h"
#endif

#include "vnctp.h"
#include "pybind11/pybind11.h"
#include "ctp/ThostFtdcTraderApi.h"


using namespace pybind11;

//����
#define ONFRONTCONNECTED 0
#define ONFRONTDISCONNECTED 1
#define ONHEARTBEATWARNING 2
#define ONRSPAUTHENTICATE 3
#define ONRSPUSERLOGIN 4
#define ONRSPUSERLOGOUT 5
#define ONRSPUSERPASSWORDUPDATE 6
#define ONRSPTRADINGACCOUNTPASSWORDUPDATE 7
#define ONRSPUSERAUTHMETHOD 8
#define ONRSPGENUSERCAPTCHA 9
#define ONRSPGENUSERTEXT 10
#define ONRSPORDERINSERT 11
#define ONRSPPARKEDORDERINSERT 12
#define ONRSPPARKEDORDERACTION 13
#define ONRSPORDERACTION 14
#define ONRSPQUERYMAXORDERVOLUME 15
#define ONRSPSETTLEMENTINFOCONFIRM 16
#define ONRSPREMOVEPARKEDORDER 17
#define ONRSPREMOVEPARKEDORDERACTION 18
#define ONRSPEXECORDERINSERT 19
#define ONRSPEXECORDERACTION 20
#define ONRSPFORQUOTEINSERT 21
#define ONRSPQUOTEINSERT 22
#define ONRSPQUOTEACTION 23
#define ONRSPBATCHORDERACTION 24
#define ONRSPOPTIONSELFCLOSEINSERT 25
#define ONRSPOPTIONSELFCLOSEACTION 26
#define ONRSPCOMBACTIONINSERT 27
#define ONRSPQRYORDER 28
#define ONRSPQRYTRADE 29
#define ONRSPQRYINVESTORPOSITION 30
#define ONRSPQRYTRADINGACCOUNT 31
#define ONRSPQRYINVESTOR 32
#define ONRSPQRYTRADINGCODE 33
#define ONRSPQRYINSTRUMENTMARGINRATE 34
#define ONRSPQRYINSTRUMENTCOMMISSIONRATE 35
#define ONRSPQRYEXCHANGE 36
#define ONRSPQRYPRODUCT 37
#define ONRSPQRYINSTRUMENT 38
#define ONRSPQRYDEPTHMARKETDATA 39
#define ONRSPQRYSETTLEMENTINFO 40
#define ONRSPQRYTRANSFERBANK 41
#define ONRSPQRYINVESTORPOSITIONDETAIL 42
#define ONRSPQRYNOTICE 43
#define ONRSPQRYSETTLEMENTINFOCONFIRM 44
#define ONRSPQRYINVESTORPOSITIONCOMBINEDETAIL 45
#define ONRSPQRYCFMMCTRADINGACCOUNTKEY 46
#define ONRSPQRYEWARRANTOFFSET 47
#define ONRSPQRYINVESTORPRODUCTGROUPMARGIN 48
#define ONRSPQRYEXCHANGEMARGINRATE 49
#define ONRSPQRYEXCHANGEMARGINRATEADJUST 50
#define ONRSPQRYEXCHANGERATE 51
#define ONRSPQRYSECAGENTACIDMAP 52
#define ONRSPQRYPRODUCTEXCHRATE 53
#define ONRSPQRYPRODUCTGROUP 54
#define ONRSPQRYMMINSTRUMENTCOMMISSIONRATE 55
#define ONRSPQRYMMOPTIONINSTRCOMMRATE 56
#define ONRSPQRYINSTRUMENTORDERCOMMRATE 57
#define ONRSPQRYSECAGENTTRADINGACCOUNT 58
#define ONRSPQRYSECAGENTCHECKMODE 59
#define ONRSPQRYSECAGENTTRADEINFO 60
#define ONRSPQRYOPTIONINSTRTRADECOST 61
#define ONRSPQRYOPTIONINSTRCOMMRATE 62
#define ONRSPQRYEXECORDER 63
#define ONRSPQRYFORQUOTE 64
#define ONRSPQRYQUOTE 65
#define ONRSPQRYOPTIONSELFCLOSE 66
#define ONRSPQRYINVESTUNIT 67
#define ONRSPQRYCOMBINSTRUMENTGUARD 68
#define ONRSPQRYCOMBACTION 69
#define ONRSPQRYTRANSFERSERIAL 70
#define ONRSPQRYACCOUNTREGISTER 71
#define ONRSPERROR 72
#define ONRTNORDER 73
#define ONRTNTRADE 74
#define ONERRRTNORDERINSERT 75
#define ONERRRTNORDERACTION 76
#define ONRTNINSTRUMENTSTATUS 77
#define ONRTNBULLETIN 78
#define ONRTNTRADINGNOTICE 79
#define ONRTNERRORCONDITIONALORDER 80
#define ONRTNEXECORDER 81
#define ONERRRTNEXECORDERINSERT 82
#define ONERRRTNEXECORDERACTION 83
#define ONERRRTNFORQUOTEINSERT 84
#define ONRTNQUOTE 85
#define ONERRRTNQUOTEINSERT 86
#define ONERRRTNQUOTEACTION 87
#define ONRTNFORQUOTERSP 88
#define ONRTNCFMMCTRADINGACCOUNTTOKEN 89
#define ONERRRTNBATCHORDERACTION 90
#define ONRTNOPTIONSELFCLOSE 91
#define ONERRRTNOPTIONSELFCLOSEINSERT 92
#define ONERRRTNOPTIONSELFCLOSEACTION 93
#define ONRTNCOMBACTION 94
#define ONERRRTNCOMBACTIONINSERT 95
#define ONRSPQRYCONTRACTBANK 96
#define ONRSPQRYPARKEDORDER 97
#define ONRSPQRYPARKEDORDERACTION 98
#define ONRSPQRYTRADINGNOTICE 99
#define ONRSPQRYBROKERTRADINGPARAMS 100
#define ONRSPQRYBROKERTRADINGALGOS 101
#define ONRSPQUERYCFMMCTRADINGACCOUNTTOKEN 102
#define ONRTNFROMBANKTOFUTUREBYBANK 103
#define ONRTNFROMFUTURETOBANKBYBANK 104
#define ONRTNREPEALFROMBANKTOFUTUREBYBANK 105
#define ONRTNREPEALFROMFUTURETOBANKBYBANK 106
#define ONRTNFROMBANKTOFUTUREBYFUTURE 107
#define ONRTNFROMFUTURETOBANKBYFUTURE 108
#define ONRTNREPEALFROMBANKTOFUTUREBYFUTUREMANUAL 109
#define ONRTNREPEALFROMFUTURETOBANKBYFUTUREMANUAL 110
#define ONRTNQUERYBANKBALANCEBYFUTURE 111
#define ONERRRTNBANKTOFUTUREBYFUTURE 112
#define ONERRRTNFUTURETOBANKBYFUTURE 113
#define ONERRRTNREPEALBANKTOFUTUREBYFUTUREMANUAL 114
#define ONERRRTNREPEALFUTURETOBANKBYFUTUREMANUAL 115
#define ONERRRTNQUERYBANKBALANCEBYFUTURE 116
#define ONRTNREPEALFROMBANKTOFUTUREBYFUTURE 117
#define ONRTNREPEALFROMFUTURETOBANKBYFUTURE 118
#define ONRSPFROMBANKTOFUTUREBYFUTURE 119
#define ONRSPFROMFUTURETOBANKBYFUTURE 120
#define ONRSPQUERYBANKACCOUNTMONEYBYFUTURE 121
#define ONRTNOPENACCOUNTBYBANK 122
#define ONRTNCANCELACCOUNTBYBANK 123
#define ONRTNCHANGEACCOUNTBYBANK 124


///-------------------------------------------------------------------------------------
///C++ SPI�Ļص���������ʵ��
///-------------------------------------------------------------------------------------

//API�ļ̳�ʵ��
class TdApi : public CThostFtdcTraderSpi
{
private:
	CThostFtdcTraderApi* api;			//API����
	thread task_thread;					//�����߳�ָ�루��python���������ݣ�
	TaskQueue task_queue;			    //�������
	bool active = false;				//����״̬

public:
	TdApi()
	{
	};

	~TdApi()
	{
		if (this->active)
		{
			this->active = false;
			this->task_thread.join();
		}
	};

	//-------------------------------------------------------------------------------------
	//API�ص�����
	//-------------------------------------------------------------------------------------

	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected() ;

	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	///@param nReason ����ԭ��
	///        0x1001 �����ʧ��
	///        0x1002 ����дʧ��
	///        0x2001 ����������ʱ
	///        0x2002 ��������ʧ��
	///        0x2003 �յ�������
	virtual void OnFrontDisconnected(int nReason) ;

	///������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
	///@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��
	virtual void OnHeartBeatWarning(int nTimeLapse) ;

	///�ͻ�����֤��Ӧ
	virtual void OnRspAuthenticate(CThostFtdcRspAuthenticateField *pRspAuthenticateField, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;


	///��¼������Ӧ
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ǳ�������Ӧ
	virtual void OnRspUserLogout(CThostFtdcUserLogoutField *pUserLogout, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�û��������������Ӧ
	virtual void OnRspUserPasswordUpdate(CThostFtdcUserPasswordUpdateField *pUserPasswordUpdate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ʽ��˻��������������Ӧ
	virtual void OnRspTradingAccountPasswordUpdate(CThostFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��ѯ�û���ǰ֧�ֵ���֤ģʽ�Ļظ�
	virtual void OnRspUserAuthMethod(CThostFtdcRspUserAuthMethodField *pRspUserAuthMethod, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��ȡͼ����֤������Ļظ�
	virtual void OnRspGenUserCaptcha(CThostFtdcRspGenUserCaptchaField *pRspGenUserCaptcha, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��ȡ������֤������Ļظ�
	virtual void OnRspGenUserText(CThostFtdcRspGenUserTextField *pRspGenUserText, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����¼��������Ӧ
	virtual void OnRspOrderInsert(CThostFtdcInputOrderField *pInputOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///Ԥ��¼��������Ӧ
	virtual void OnRspParkedOrderInsert(CThostFtdcParkedOrderField *pParkedOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///Ԥ�񳷵�¼��������Ӧ
	virtual void OnRspParkedOrderAction(CThostFtdcParkedOrderActionField *pParkedOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��������������Ӧ
	virtual void OnRspOrderAction(CThostFtdcInputOrderActionField *pInputOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��ѯ��󱨵�������Ӧ
	virtual void OnRspQueryMaxOrderVolume(CThostFtdcQueryMaxOrderVolumeField *pQueryMaxOrderVolume, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///Ͷ���߽�����ȷ����Ӧ
	virtual void OnRspSettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///ɾ��Ԥ����Ӧ
	virtual void OnRspRemoveParkedOrder(CThostFtdcRemoveParkedOrderField *pRemoveParkedOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///ɾ��Ԥ�񳷵���Ӧ
	virtual void OnRspRemoveParkedOrderAction(CThostFtdcRemoveParkedOrderActionField *pRemoveParkedOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///ִ������¼��������Ӧ
	virtual void OnRspExecOrderInsert(CThostFtdcInputExecOrderField *pInputExecOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///ִ���������������Ӧ
	virtual void OnRspExecOrderAction(CThostFtdcInputExecOrderActionField *pInputExecOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///ѯ��¼��������Ӧ
	virtual void OnRspForQuoteInsert(CThostFtdcInputForQuoteField *pInputForQuote, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����¼��������Ӧ
	virtual void OnRspQuoteInsert(CThostFtdcInputQuoteField *pInputQuote, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///���۲���������Ӧ
	virtual void OnRspQuoteAction(CThostFtdcInputQuoteActionField *pInputQuoteAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///������������������Ӧ
	virtual void OnRspBatchOrderAction(CThostFtdcInputBatchOrderActionField *pInputBatchOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��Ȩ�ԶԳ�¼��������Ӧ
	virtual void OnRspOptionSelfCloseInsert(CThostFtdcInputOptionSelfCloseField *pInputOptionSelfClose, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��Ȩ�ԶԳ����������Ӧ
	virtual void OnRspOptionSelfCloseAction(CThostFtdcInputOptionSelfCloseActionField *pInputOptionSelfCloseAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�������¼��������Ӧ
	virtual void OnRspCombActionInsert(CThostFtdcInputCombActionField *pInputCombAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������Ӧ
	virtual void OnRspQryOrder(CThostFtdcOrderField *pOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ɽ���Ӧ
	virtual void OnRspQryTrade(CThostFtdcTradeField *pTrade, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ���ֲ߳���Ӧ
	virtual void OnRspQryInvestorPosition(CThostFtdcInvestorPositionField *pInvestorPosition, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ʽ��˻���Ӧ
	virtual void OnRspQryTradingAccount(CThostFtdcTradingAccountField *pTradingAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ������Ӧ
	virtual void OnRspQryInvestor(CThostFtdcInvestorField *pInvestor, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ���ױ�����Ӧ
	virtual void OnRspQryTradingCode(CThostFtdcTradingCodeField *pTradingCode, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Լ��֤������Ӧ
	virtual void OnRspQryInstrumentMarginRate(CThostFtdcInstrumentMarginRateField *pInstrumentMarginRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Լ����������Ӧ
	virtual void OnRspQryInstrumentCommissionRate(CThostFtdcInstrumentCommissionRateField *pInstrumentCommissionRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��������Ӧ
	virtual void OnRspQryExchange(CThostFtdcExchangeField *pExchange, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ʒ��Ӧ
	virtual void OnRspQryProduct(CThostFtdcProductField *pProduct, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Լ��Ӧ
	virtual void OnRspQryInstrument(CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������Ӧ
	virtual void OnRspQryDepthMarketData(CThostFtdcDepthMarketDataField *pDepthMarketData, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ���߽�������Ӧ
	virtual void OnRspQrySettlementInfo(CThostFtdcSettlementInfoField *pSettlementInfo, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯת��������Ӧ
	virtual void OnRspQryTransferBank(CThostFtdcTransferBankField *pTransferBank, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ���ֲ߳���ϸ��Ӧ
	virtual void OnRspQryInvestorPositionDetail(CThostFtdcInvestorPositionDetailField *pInvestorPositionDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ͻ�֪ͨ��Ӧ
	virtual void OnRspQryNotice(CThostFtdcNoticeField *pNotice, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������Ϣȷ����Ӧ
	virtual void OnRspQrySettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ���ֲ߳���ϸ��Ӧ
	virtual void OnRspQryInvestorPositionCombineDetail(CThostFtdcInvestorPositionCombineDetailField *pInvestorPositionCombineDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��ѯ��֤����ϵͳ���͹�˾�ʽ��˻���Կ��Ӧ
	virtual void OnRspQryCFMMCTradingAccountKey(CThostFtdcCFMMCTradingAccountKeyField *pCFMMCTradingAccountKey, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ֵ��۵���Ϣ��Ӧ
	virtual void OnRspQryEWarrantOffset(CThostFtdcEWarrantOffsetField *pEWarrantOffset, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ����Ʒ��/��Ʒ�ֱ�֤����Ӧ
	virtual void OnRspQryInvestorProductGroupMargin(CThostFtdcInvestorProductGroupMarginField *pInvestorProductGroupMargin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��������֤������Ӧ
	virtual void OnRspQryExchangeMarginRate(CThostFtdcExchangeMarginRateField *pExchangeMarginRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������������֤������Ӧ
	virtual void OnRspQryExchangeMarginRateAdjust(CThostFtdcExchangeMarginRateAdjustField *pExchangeMarginRateAdjust, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������Ӧ
	virtual void OnRspQryExchangeRate(CThostFtdcExchangeRateField *pExchangeRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�����������Ա����Ȩ����Ӧ
	virtual void OnRspQrySecAgentACIDMap(CThostFtdcSecAgentACIDMapField *pSecAgentACIDMap, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ʒ���ۻ���
	virtual void OnRspQryProductExchRate(CThostFtdcProductExchRateField *pProductExchRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ʒ��
	virtual void OnRspQryProductGroup(CThostFtdcProductGroupField *pProductGroup, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�����̺�Լ����������Ӧ
	virtual void OnRspQryMMInstrumentCommissionRate(CThostFtdcMMInstrumentCommissionRateField *pMMInstrumentCommissionRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��������Ȩ��Լ��������Ӧ
	virtual void OnRspQryMMOptionInstrCommRate(CThostFtdcMMOptionInstrCommRateField *pMMOptionInstrCommRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������������Ӧ
	virtual void OnRspQryInstrumentOrderCommRate(CThostFtdcInstrumentOrderCommRateField *pInstrumentOrderCommRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ʽ��˻���Ӧ
	virtual void OnRspQrySecAgentTradingAccount(CThostFtdcTradingAccountField *pTradingAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�����������ʽ�У��ģʽ��Ӧ
	virtual void OnRspQrySecAgentCheckMode(CThostFtdcSecAgentCheckModeField *pSecAgentCheckMode, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������������Ϣ��Ӧ
	virtual void OnRspQrySecAgentTradeInfo(CThostFtdcSecAgentTradeInfoField *pSecAgentTradeInfo, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ȩ���׳ɱ���Ӧ
	virtual void OnRspQryOptionInstrTradeCost(CThostFtdcOptionInstrTradeCostField *pOptionInstrTradeCost, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ȩ��Լ��������Ӧ
	virtual void OnRspQryOptionInstrCommRate(CThostFtdcOptionInstrCommRateField *pOptionInstrCommRate, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯִ��������Ӧ
	virtual void OnRspQryExecOrder(CThostFtdcExecOrderField *pExecOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯѯ����Ӧ
	virtual void OnRspQryForQuote(CThostFtdcForQuoteField *pForQuote, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ������Ӧ
	virtual void OnRspQryQuote(CThostFtdcQuoteField *pQuote, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ȩ�ԶԳ���Ӧ
	virtual void OnRspQryOptionSelfClose(CThostFtdcOptionSelfCloseField *pOptionSelfClose, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ�ʵ�Ԫ��Ӧ
	virtual void OnRspQryInvestUnit(CThostFtdcInvestUnitField *pInvestUnit, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��Ϻ�Լ��ȫϵ����Ӧ
	virtual void OnRspQryCombInstrumentGuard(CThostFtdcCombInstrumentGuardField *pCombInstrumentGuard, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ���������Ӧ
	virtual void OnRspQryCombAction(CThostFtdcCombActionField *pCombAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯת����ˮ��Ӧ
	virtual void OnRspQryTransferSerial(CThostFtdcTransferSerialField *pTransferSerial, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ����ǩԼ��ϵ��Ӧ
	virtual void OnRspQryAccountregister(CThostFtdcAccountregisterField *pAccountregister, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����Ӧ��
	virtual void OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����֪ͨ
	virtual void OnRtnOrder(CThostFtdcOrderField *pOrder) ;

	///�ɽ�֪ͨ
	virtual void OnRtnTrade(CThostFtdcTradeField *pTrade) ;

	///����¼�����ر�
	virtual void OnErrRtnOrderInsert(CThostFtdcInputOrderField *pInputOrder, CThostFtdcRspInfoField *pRspInfo) ;

	///������������ر�
	virtual void OnErrRtnOrderAction(CThostFtdcOrderActionField *pOrderAction, CThostFtdcRspInfoField *pRspInfo) ;

	///��Լ����״̬֪ͨ
	virtual void OnRtnInstrumentStatus(CThostFtdcInstrumentStatusField *pInstrumentStatus) ;

	///����������֪ͨ
	virtual void OnRtnBulletin(CThostFtdcBulletinField *pBulletin) ;

	///����֪ͨ
	virtual void OnRtnTradingNotice(CThostFtdcTradingNoticeInfoField *pTradingNoticeInfo) ;

	///��ʾ������У�����
	virtual void OnRtnErrorConditionalOrder(CThostFtdcErrorConditionalOrderField *pErrorConditionalOrder) ;

	///ִ������֪ͨ
	virtual void OnRtnExecOrder(CThostFtdcExecOrderField *pExecOrder) ;

	///ִ������¼�����ر�
	virtual void OnErrRtnExecOrderInsert(CThostFtdcInputExecOrderField *pInputExecOrder, CThostFtdcRspInfoField *pRspInfo) ;

	///ִ�������������ر�
	virtual void OnErrRtnExecOrderAction(CThostFtdcExecOrderActionField *pExecOrderAction, CThostFtdcRspInfoField *pRspInfo) ;

	///ѯ��¼�����ر�
	virtual void OnErrRtnForQuoteInsert(CThostFtdcInputForQuoteField *pInputForQuote, CThostFtdcRspInfoField *pRspInfo) ;

	///����֪ͨ
	virtual void OnRtnQuote(CThostFtdcQuoteField *pQuote) ;

	///����¼�����ر�
	virtual void OnErrRtnQuoteInsert(CThostFtdcInputQuoteField *pInputQuote, CThostFtdcRspInfoField *pRspInfo) ;

	///���۲�������ر�
	virtual void OnErrRtnQuoteAction(CThostFtdcQuoteActionField *pQuoteAction, CThostFtdcRspInfoField *pRspInfo) ;

	///ѯ��֪ͨ
	virtual void OnRtnForQuoteRsp(CThostFtdcForQuoteRspField *pForQuoteRsp) ;

	///��֤���������û�����
	virtual void OnRtnCFMMCTradingAccountToken(CThostFtdcCFMMCTradingAccountTokenField *pCFMMCTradingAccountToken) ;

	///����������������ر�
	virtual void OnErrRtnBatchOrderAction(CThostFtdcBatchOrderActionField *pBatchOrderAction, CThostFtdcRspInfoField *pRspInfo) ;

	///��Ȩ�ԶԳ�֪ͨ
	virtual void OnRtnOptionSelfClose(CThostFtdcOptionSelfCloseField *pOptionSelfClose) ;

	///��Ȩ�ԶԳ�¼�����ر�
	virtual void OnErrRtnOptionSelfCloseInsert(CThostFtdcInputOptionSelfCloseField *pInputOptionSelfClose, CThostFtdcRspInfoField *pRspInfo) ;

	///��Ȩ�ԶԳ��������ر�
	virtual void OnErrRtnOptionSelfCloseAction(CThostFtdcOptionSelfCloseActionField *pOptionSelfCloseAction, CThostFtdcRspInfoField *pRspInfo) ;

	///�������֪ͨ
	virtual void OnRtnCombAction(CThostFtdcCombActionField *pCombAction) ;

	///�������¼�����ر�
	virtual void OnErrRtnCombActionInsert(CThostFtdcInputCombActionField *pInputCombAction, CThostFtdcRspInfoField *pRspInfo) ;

	///�����ѯǩԼ������Ӧ
	virtual void OnRspQryContractBank(CThostFtdcContractBankField *pContractBank, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯԤ����Ӧ
	virtual void OnRspQryParkedOrder(CThostFtdcParkedOrderField *pParkedOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯԤ�񳷵���Ӧ
	virtual void OnRspQryParkedOrderAction(CThostFtdcParkedOrderActionField *pParkedOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ����֪ͨ��Ӧ
	virtual void OnRspQryTradingNotice(CThostFtdcTradingNoticeField *pTradingNotice, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ���͹�˾���ײ�����Ӧ
	virtual void OnRspQryBrokerTradingParams(CThostFtdcBrokerTradingParamsField *pBrokerTradingParams, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ���͹�˾�����㷨��Ӧ
	virtual void OnRspQryBrokerTradingAlgos(CThostFtdcBrokerTradingAlgosField *pBrokerTradingAlgos, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ��������û�����
	virtual void OnRspQueryCFMMCTradingAccountToken(CThostFtdcQueryCFMMCTradingAccountTokenField *pQueryCFMMCTradingAccountToken, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///���з��������ʽ�ת�ڻ�֪ͨ
	virtual void OnRtnFromBankToFutureByBank(CThostFtdcRspTransferField *pRspTransfer) ;

	///���з����ڻ��ʽ�ת����֪ͨ
	virtual void OnRtnFromFutureToBankByBank(CThostFtdcRspTransferField *pRspTransfer) ;

	///���з����������ת�ڻ�֪ͨ
	virtual void OnRtnRepealFromBankToFutureByBank(CThostFtdcRspRepealField *pRspRepeal) ;

	///���з�������ڻ�ת����֪ͨ
	virtual void OnRtnRepealFromFutureToBankByBank(CThostFtdcRspRepealField *pRspRepeal) ;

	///�ڻ����������ʽ�ת�ڻ�֪ͨ
	virtual void OnRtnFromBankToFutureByFuture(CThostFtdcRspTransferField *pRspTransfer) ;

	///�ڻ������ڻ��ʽ�ת����֪ͨ
	virtual void OnRtnFromFutureToBankByFuture(CThostFtdcRspTransferField *pRspTransfer) ;

	///ϵͳ����ʱ�ڻ����ֹ������������ת�ڻ��������д�����Ϻ��̷��ص�֪ͨ
	virtual void OnRtnRepealFromBankToFutureByFutureManual(CThostFtdcRspRepealField *pRspRepeal) ;

	///ϵͳ����ʱ�ڻ����ֹ���������ڻ�ת�����������д�����Ϻ��̷��ص�֪ͨ
	virtual void OnRtnRepealFromFutureToBankByFutureManual(CThostFtdcRspRepealField *pRspRepeal) ;

	///�ڻ������ѯ�������֪ͨ
	virtual void OnRtnQueryBankBalanceByFuture(CThostFtdcNotifyQueryAccountField *pNotifyQueryAccount) ;

	///�ڻ����������ʽ�ת�ڻ�����ر�
	virtual void OnErrRtnBankToFutureByFuture(CThostFtdcReqTransferField *pReqTransfer, CThostFtdcRspInfoField *pRspInfo) ;

	///�ڻ������ڻ��ʽ�ת���д���ر�
	virtual void OnErrRtnFutureToBankByFuture(CThostFtdcReqTransferField *pReqTransfer, CThostFtdcRspInfoField *pRspInfo) ;

	///ϵͳ����ʱ�ڻ����ֹ������������ת�ڻ�����ر�
	virtual void OnErrRtnRepealBankToFutureByFutureManual(CThostFtdcReqRepealField *pReqRepeal, CThostFtdcRspInfoField *pRspInfo) ;

	///ϵͳ����ʱ�ڻ����ֹ���������ڻ�ת���д���ر�
	virtual void OnErrRtnRepealFutureToBankByFutureManual(CThostFtdcReqRepealField *pReqRepeal, CThostFtdcRspInfoField *pRspInfo) ;

	///�ڻ������ѯ����������ر�
	virtual void OnErrRtnQueryBankBalanceByFuture(CThostFtdcReqQueryAccountField *pReqQueryAccount, CThostFtdcRspInfoField *pRspInfo) ;

	///�ڻ������������ת�ڻ��������д�����Ϻ��̷��ص�֪ͨ
	virtual void OnRtnRepealFromBankToFutureByFuture(CThostFtdcRspRepealField *pRspRepeal) ;

	///�ڻ���������ڻ�ת�����������д�����Ϻ��̷��ص�֪ͨ
	virtual void OnRtnRepealFromFutureToBankByFuture(CThostFtdcRspRepealField *pRspRepeal) ;

	///�ڻ����������ʽ�ת�ڻ�Ӧ��
	virtual void OnRspFromBankToFutureByFuture(CThostFtdcReqTransferField *pReqTransfer, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ڻ������ڻ��ʽ�ת����Ӧ��
	virtual void OnRspFromFutureToBankByFuture(CThostFtdcReqTransferField *pReqTransfer, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ڻ������ѯ�������Ӧ��
	virtual void OnRspQueryBankAccountMoneyByFuture(CThostFtdcReqQueryAccountField *pReqQueryAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///���з������ڿ���֪ͨ
	virtual void OnRtnOpenAccountByBank(CThostFtdcOpenAccountField *pOpenAccount) ;

	///���з�����������֪ͨ
	virtual void OnRtnCancelAccountByBank(CThostFtdcCancelAccountField *pCancelAccount) ;

	///���з����������˺�֪ͨ
	virtual void OnRtnChangeAccountByBank(CThostFtdcChangeAccountField *pChangeAccount) ;

	//-------------------------------------------------------------------------------------
	//task������
	//-------------------------------------------------------------------------------------

	void processTask();

	void processFrontConnected(Task *task);

	void processFrontDisconnected(Task *task);

	void processHeartBeatWarning(Task *task);

	void processRspAuthenticate(Task *task);

	void processRspUserLogin(Task *task);

	void processRspUserLogout(Task *task);

	void processRspUserPasswordUpdate(Task *task);

	void processRspTradingAccountPasswordUpdate(Task *task);

	void processRspUserAuthMethod(Task *task);

	void processRspGenUserCaptcha(Task *task);

	void processRspGenUserText(Task *task);

	void processRspOrderInsert(Task *task);

	void processRspParkedOrderInsert(Task *task);

	void processRspParkedOrderAction(Task *task);

	void processRspOrderAction(Task *task);

	void processRspQueryMaxOrderVolume(Task *task);

	void processRspSettlementInfoConfirm(Task *task);

	void processRspRemoveParkedOrder(Task *task);

	void processRspRemoveParkedOrderAction(Task *task);

	void processRspExecOrderInsert(Task *task);

	void processRspExecOrderAction(Task *task);

	void processRspForQuoteInsert(Task *task);

	void processRspQuoteInsert(Task *task);

	void processRspQuoteAction(Task *task);

	void processRspBatchOrderAction(Task *task);

	void processRspOptionSelfCloseInsert(Task *task);

	void processRspOptionSelfCloseAction(Task *task);

	void processRspCombActionInsert(Task *task);

	void processRspQryOrder(Task *task);

	void processRspQryTrade(Task *task);

	void processRspQryInvestorPosition(Task *task);

	void processRspQryTradingAccount(Task *task);

	void processRspQryInvestor(Task *task);

	void processRspQryTradingCode(Task *task);

	void processRspQryInstrumentMarginRate(Task *task);

	void processRspQryInstrumentCommissionRate(Task *task);

	void processRspQryExchange(Task *task);

	void processRspQryProduct(Task *task);

	void processRspQryInstrument(Task *task);

	void processRspQryDepthMarketData(Task *task);

	void processRspQrySettlementInfo(Task *task);

	void processRspQryTransferBank(Task *task);

	void processRspQryInvestorPositionDetail(Task *task);

	void processRspQryNotice(Task *task);

	void processRspQrySettlementInfoConfirm(Task *task);

	void processRspQryInvestorPositionCombineDetail(Task *task);

	void processRspQryCFMMCTradingAccountKey(Task *task);

	void processRspQryEWarrantOffset(Task *task);

	void processRspQryInvestorProductGroupMargin(Task *task);

	void processRspQryExchangeMarginRate(Task *task);

	void processRspQryExchangeMarginRateAdjust(Task *task);

	void processRspQryExchangeRate(Task *task);

	void processRspQrySecAgentACIDMap(Task *task);

	void processRspQryProductExchRate(Task *task);

	void processRspQryProductGroup(Task *task);

	void processRspQryMMInstrumentCommissionRate(Task *task);

	void processRspQryMMOptionInstrCommRate(Task *task);

	void processRspQryInstrumentOrderCommRate(Task *task);

	void processRspQrySecAgentTradingAccount(Task *task);

	void processRspQrySecAgentCheckMode(Task *task);

	void processRspQrySecAgentTradeInfo(Task *task);

	void processRspQryOptionInstrTradeCost(Task *task);

	void processRspQryOptionInstrCommRate(Task *task);

	void processRspQryExecOrder(Task *task);

	void processRspQryForQuote(Task *task);

	void processRspQryQuote(Task *task);

	void processRspQryOptionSelfClose(Task *task);

	void processRspQryInvestUnit(Task *task);

	void processRspQryCombInstrumentGuard(Task *task);

	void processRspQryCombAction(Task *task);

	void processRspQryTransferSerial(Task *task);

	void processRspQryAccountregister(Task *task);

	void processRspError(Task *task);

	void processRtnOrder(Task *task);

	void processRtnTrade(Task *task);

	void processErrRtnOrderInsert(Task *task);

	void processErrRtnOrderAction(Task *task);

	void processRtnInstrumentStatus(Task *task);

	void processRtnBulletin(Task *task);

	void processRtnTradingNotice(Task *task);

	void processRtnErrorConditionalOrder(Task *task);

	void processRtnExecOrder(Task *task);

	void processErrRtnExecOrderInsert(Task *task);

	void processErrRtnExecOrderAction(Task *task);

	void processErrRtnForQuoteInsert(Task *task);

	void processRtnQuote(Task *task);

	void processErrRtnQuoteInsert(Task *task);

	void processErrRtnQuoteAction(Task *task);

	void processRtnForQuoteRsp(Task *task);

	void processRtnCFMMCTradingAccountToken(Task *task);

	void processErrRtnBatchOrderAction(Task *task);

	void processRtnOptionSelfClose(Task *task);

	void processErrRtnOptionSelfCloseInsert(Task *task);

	void processErrRtnOptionSelfCloseAction(Task *task);

	void processRtnCombAction(Task *task);

	void processErrRtnCombActionInsert(Task *task);

	void processRspQryContractBank(Task *task);

	void processRspQryParkedOrder(Task *task);

	void processRspQryParkedOrderAction(Task *task);

	void processRspQryTradingNotice(Task *task);

	void processRspQryBrokerTradingParams(Task *task);

	void processRspQryBrokerTradingAlgos(Task *task);

	void processRspQueryCFMMCTradingAccountToken(Task *task);

	void processRtnFromBankToFutureByBank(Task *task);

	void processRtnFromFutureToBankByBank(Task *task);

	void processRtnRepealFromBankToFutureByBank(Task *task);

	void processRtnRepealFromFutureToBankByBank(Task *task);

	void processRtnFromBankToFutureByFuture(Task *task);

	void processRtnFromFutureToBankByFuture(Task *task);

	void processRtnRepealFromBankToFutureByFutureManual(Task *task);

	void processRtnRepealFromFutureToBankByFutureManual(Task *task);

	void processRtnQueryBankBalanceByFuture(Task *task);

	void processErrRtnBankToFutureByFuture(Task *task);

	void processErrRtnFutureToBankByFuture(Task *task);

	void processErrRtnRepealBankToFutureByFutureManual(Task *task);

	void processErrRtnRepealFutureToBankByFutureManual(Task *task);

	void processErrRtnQueryBankBalanceByFuture(Task *task);

	void processRtnRepealFromBankToFutureByFuture(Task *task);

	void processRtnRepealFromFutureToBankByFuture(Task *task);

	void processRspFromBankToFutureByFuture(Task *task);

	void processRspFromFutureToBankByFuture(Task *task);

	void processRspQueryBankAccountMoneyByFuture(Task *task);

	void processRtnOpenAccountByBank(Task *task);

	void processRtnCancelAccountByBank(Task *task);

	void processRtnChangeAccountByBank(Task *task);


	//-------------------------------------------------------------------------------------
	//data���ص������������ֵ�
	//error���ص������Ĵ����ֵ�
	//id������id
	//last���Ƿ�Ϊ��󷵻�
	//i������
	//-------------------------------------------------------------------------------------

	virtual void onFrontConnected() {};

	virtual void onFrontDisconnected(int reqid) {};

	virtual void onHeartBeatWarning(int reqid) {};

	virtual void onRspAuthenticate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspUserLogin(dict data, dict error, int reqid, bool last) {};

	virtual void onRspUserLogout(dict data, dict error, int reqid, bool last) {};

	virtual void onRspUserPasswordUpdate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspTradingAccountPasswordUpdate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspUserAuthMethod(dict data, dict error, int reqid, bool last) {};

	virtual void onRspGenUserCaptcha(dict data, dict error, int reqid, bool last) {};

	virtual void onRspGenUserText(dict data, dict error, int reqid, bool last) {};

	virtual void onRspOrderInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspParkedOrderInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspParkedOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQueryMaxOrderVolume(dict data, dict error, int reqid, bool last) {};

	virtual void onRspSettlementInfoConfirm(dict data, dict error, int reqid, bool last) {};

	virtual void onRspRemoveParkedOrder(dict data, dict error, int reqid, bool last) {};

	virtual void onRspRemoveParkedOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspExecOrderInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspExecOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspForQuoteInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQuoteInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQuoteAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspBatchOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspOptionSelfCloseInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspOptionSelfCloseAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspCombActionInsert(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryOrder(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTrade(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestorPosition(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTradingAccount(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestor(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTradingCode(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInstrumentMarginRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInstrumentCommissionRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryExchange(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryProduct(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInstrument(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryDepthMarketData(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySettlementInfo(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTransferBank(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestorPositionDetail(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryNotice(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySettlementInfoConfirm(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestorPositionCombineDetail(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryCFMMCTradingAccountKey(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryEWarrantOffset(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestorProductGroupMargin(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryExchangeMarginRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryExchangeMarginRateAdjust(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryExchangeRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySecAgentACIDMap(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryProductExchRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryProductGroup(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryMMInstrumentCommissionRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryMMOptionInstrCommRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInstrumentOrderCommRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySecAgentTradingAccount(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySecAgentCheckMode(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQrySecAgentTradeInfo(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryOptionInstrTradeCost(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryOptionInstrCommRate(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryExecOrder(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryForQuote(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryQuote(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryOptionSelfClose(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryInvestUnit(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryCombInstrumentGuard(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryCombAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTransferSerial(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryAccountregister(dict data, dict error, int reqid, bool last) {};

	virtual void onRspError(dict error, int reqid, bool last) {};

	virtual void onRtnOrder(dict data) {};

	virtual void onRtnTrade(dict data) {};

	virtual void onErrRtnOrderInsert(dict data, dict error) {};

	virtual void onErrRtnOrderAction(dict data, dict error) {};

	virtual void onRtnInstrumentStatus(dict data) {};

	virtual void onRtnBulletin(dict data) {};

	virtual void onRtnTradingNotice(dict data) {};

	virtual void onRtnErrorConditionalOrder(dict data) {};

	virtual void onRtnExecOrder(dict data) {};

	virtual void onErrRtnExecOrderInsert(dict data, dict error) {};

	virtual void onErrRtnExecOrderAction(dict data, dict error) {};

	virtual void onErrRtnForQuoteInsert(dict data, dict error) {};

	virtual void onRtnQuote(dict data) {};

	virtual void onErrRtnQuoteInsert(dict data, dict error) {};

	virtual void onErrRtnQuoteAction(dict data, dict error) {};

	virtual void onRtnForQuoteRsp(dict data) {};

	virtual void onRtnCFMMCTradingAccountToken(dict data) {};

	virtual void onErrRtnBatchOrderAction(dict data, dict error) {};

	virtual void onRtnOptionSelfClose(dict data) {};

	virtual void onErrRtnOptionSelfCloseInsert(dict data, dict error) {};

	virtual void onErrRtnOptionSelfCloseAction(dict data, dict error) {};

	virtual void onRtnCombAction(dict data) {};

	virtual void onErrRtnCombActionInsert(dict data, dict error) {};

	virtual void onRspQryContractBank(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryParkedOrder(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryParkedOrderAction(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryTradingNotice(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryBrokerTradingParams(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQryBrokerTradingAlgos(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQueryCFMMCTradingAccountToken(dict data, dict error, int reqid, bool last) {};

	virtual void onRtnFromBankToFutureByBank(dict data) {};

	virtual void onRtnFromFutureToBankByBank(dict data) {};

	virtual void onRtnRepealFromBankToFutureByBank(dict data) {};

	virtual void onRtnRepealFromFutureToBankByBank(dict data) {};

	virtual void onRtnFromBankToFutureByFuture(dict data) {};

	virtual void onRtnFromFutureToBankByFuture(dict data) {};

	virtual void onRtnRepealFromBankToFutureByFutureManual(dict data) {};

	virtual void onRtnRepealFromFutureToBankByFutureManual(dict data) {};

	virtual void onRtnQueryBankBalanceByFuture(dict data) {};

	virtual void onErrRtnBankToFutureByFuture(dict data, dict error) {};

	virtual void onErrRtnFutureToBankByFuture(dict data, dict error) {};

	virtual void onErrRtnRepealBankToFutureByFutureManual(dict data, dict error) {};

	virtual void onErrRtnRepealFutureToBankByFutureManual(dict data, dict error) {};

	virtual void onErrRtnQueryBankBalanceByFuture(dict data, dict error) {};

	virtual void onRtnRepealFromBankToFutureByFuture(dict data) {};

	virtual void onRtnRepealFromFutureToBankByFuture(dict data) {};

	virtual void onRspFromBankToFutureByFuture(dict data, dict error, int reqid, bool last) {};

	virtual void onRspFromFutureToBankByFuture(dict data, dict error, int reqid, bool last) {};

	virtual void onRspQueryBankAccountMoneyByFuture(dict data, dict error, int reqid, bool last) {};

	virtual void onRtnOpenAccountByBank(dict data) {};

	virtual void onRtnCancelAccountByBank(dict data) {};

	virtual void onRtnChangeAccountByBank(dict data) {};

	//-------------------------------------------------------------------------------------
	//req:���������������ֵ�
	//-------------------------------------------------------------------------------------

	void createFtdcTraderApi(string pszFlowPath = "");

	void release();

	void init();

	int join();

	int exit();

	string getTradingDay();

	void registerFront(string pszFrontAddress);

	void subscribePrivateTopic(int nType);

	void subscribePublicTopic(int nType);

	int reqAuthenticate(dict req, int reqid);

	int reqUserLogin(dict req, int reqid);

	int reqUserLogout(dict req, int reqid);

	int reqUserPasswordUpdate(dict req, int reqid);

	int reqTradingAccountPasswordUpdate(dict req, int reqid);

	int reqUserAuthMethod(dict req, int reqid);

	int reqGenUserCaptcha(dict req, int reqid);

	int reqGenUserText(dict req, int reqid);

	int reqUserLoginWithCaptcha(dict req, int reqid);

	int reqUserLoginWithText(dict req, int reqid);

	int reqUserLoginWithOTP(dict req, int reqid);

	int reqOrderInsert(dict req, int reqid);

	int reqParkedOrderInsert(dict req, int reqid);

	int reqParkedOrderAction(dict req, int reqid);

	int reqOrderAction(dict req, int reqid);

	int reqQueryMaxOrderVolume(dict req, int reqid);

	int reqSettlementInfoConfirm(dict req, int reqid);

	int reqRemoveParkedOrder(dict req, int reqid);

	int reqRemoveParkedOrderAction(dict req, int reqid);

	int reqExecOrderInsert(dict req, int reqid);

	int reqExecOrderAction(dict req, int reqid);

	int reqForQuoteInsert(dict req, int reqid);

	int reqQuoteInsert(dict req, int reqid);

	int reqQuoteAction(dict req, int reqid);

	int reqBatchOrderAction(dict req, int reqid);

	int reqOptionSelfCloseInsert(dict req, int reqid);

	int reqOptionSelfCloseAction(dict req, int reqid);

	int reqCombActionInsert(dict req, int reqid);

	int reqQryOrder(dict req, int reqid);

	int reqQryTrade(dict req, int reqid);

	int reqQryInvestorPosition(dict req, int reqid);

	int reqQryTradingAccount(dict req, int reqid);

	int reqQryInvestor(dict req, int reqid);

	int reqQryTradingCode(dict req, int reqid);

	int reqQryInstrumentMarginRate(dict req, int reqid);

	int reqQryInstrumentCommissionRate(dict req, int reqid);

	int reqQryExchange(dict req, int reqid);

	int reqQryProduct(dict req, int reqid);

	int reqQryInstrument(dict req, int reqid);

	int reqQryDepthMarketData(dict req, int reqid);

	int reqQrySettlementInfo(dict req, int reqid);

	int reqQryTransferBank(dict req, int reqid);

	int reqQryInvestorPositionDetail(dict req, int reqid);

	int reqQryNotice(dict req, int reqid);

	int reqQrySettlementInfoConfirm(dict req, int reqid);

	int reqQryInvestorPositionCombineDetail(dict req, int reqid);

	int reqQryCFMMCTradingAccountKey(dict req, int reqid);

	int reqQryEWarrantOffset(dict req, int reqid);

	int reqQryInvestorProductGroupMargin(dict req, int reqid);

	int reqQryExchangeMarginRate(dict req, int reqid);

	int reqQryExchangeMarginRateAdjust(dict req, int reqid);

	int reqQryExchangeRate(dict req, int reqid);

	int reqQrySecAgentACIDMap(dict req, int reqid);

	int reqQryProductExchRate(dict req, int reqid);

	int reqQryProductGroup(dict req, int reqid);

	int reqQryMMInstrumentCommissionRate(dict req, int reqid);

	int reqQryMMOptionInstrCommRate(dict req, int reqid);

	int reqQryInstrumentOrderCommRate(dict req, int reqid);

	int reqQrySecAgentTradingAccount(dict req, int reqid);

	int reqQrySecAgentCheckMode(dict req, int reqid);

	int reqQrySecAgentTradeInfo(dict req, int reqid);

	int reqQryOptionInstrTradeCost(dict req, int reqid);

	int reqQryOptionInstrCommRate(dict req, int reqid);

	int reqQryExecOrder(dict req, int reqid);

	int reqQryForQuote(dict req, int reqid);

	int reqQryQuote(dict req, int reqid);

	int reqQryOptionSelfClose(dict req, int reqid);

	int reqQryInvestUnit(dict req, int reqid);

	int reqQryCombInstrumentGuard(dict req, int reqid);

	int reqQryCombAction(dict req, int reqid);

	int reqQryTransferSerial(dict req, int reqid);

	int reqQryAccountregister(dict req, int reqid);

	int reqQryContractBank(dict req, int reqid);

	int reqQryParkedOrder(dict req, int reqid);

	int reqQryParkedOrderAction(dict req, int reqid);

	int reqQryTradingNotice(dict req, int reqid);

	int reqQryBrokerTradingParams(dict req, int reqid);

	int reqQryBrokerTradingAlgos(dict req, int reqid);

	int reqQueryCFMMCTradingAccountToken(dict req, int reqid);

	int reqFromBankToFutureByFuture(dict req, int reqid);

	int reqFromFutureToBankByFuture(dict req, int reqid);

	int reqQueryBankAccountMoneyByFuture(dict req, int reqid);
};
