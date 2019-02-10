#define NOMINMAX
#define _CRT_SECURE_NO_WARNINGS

#include <string>
#include <queue>
#include <thread>
#include <mutex>
#include <iostream>
#include <codecvt>

#include "pybind11/pybind11.h"


using namespace std;
using namespace pybind11;


//����ṹ��
struct Task
{
	int task_name;		//�ص��������ƶ�Ӧ�ĳ���
	void *task_data;	//����ָ��
	void *task_error;	//����ָ��
	int task_id;		//����id
	bool task_last;		//�Ƿ�Ϊ��󷵻�
};


class TaskQueue
{
private:
	queue<Task> queue_;						//��׼�����
	mutex mutex_;							//������
	condition_variable cond_;				//��������

public:

	//�����µ�����
	void push(const Task &task)
	{
		unique_lock<mutex > mlock(mutex_);
		queue_.push(task);					//������д�������
		mlock.unlock();						//�ͷ���
		cond_.notify_one();					//֪ͨ���������ȴ����߳�
	}

	//ȡ���ϵ�����
	Task pop()
	{
		unique_lock<mutex> mlock(mutex_);
		while (queue_.empty())				//������Ϊ��ʱ
		{
			cond_.wait(mlock);				//�ȴ���������֪ͨ
		}
		Task task = queue_.front();			//��ȡ�����е����һ������
		queue_.pop();						//ɾ��������
		return task;						//���ظ�����
	}

};


//���ֵ��л�ȡĳ����ֵ��Ӧ������������ֵ������ṹ������ֵ��
void getInt(dict d, const char *key, int *value)
{
	if (d.contains(key))		//����ֵ����Ƿ���ڸü�ֵ
	{
		object o = d[key];		//��ȡ�ü�ֵ
		try
		{
			*value = o.cast<int>();
		}
		catch (const error_already_set &e)
		{
			cout << e.what() << endl;
		}
	}
};


//���ֵ��л�ȡĳ����ֵ��Ӧ�ĸ�����������ֵ������ṹ������ֵ��
void getDouble(dict d, const char *key, double *value)
{
	if (d.contains(key))
	{
		object o = d[key];
		try
		{
			*value = o.cast<double>();
		}
		catch (const error_already_set &e)
		{
			cout << e.what() << endl;
		}
	}
};


//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ�������ֵ������ṹ������ֵ��
void getChar(dict d, const char *key, char *value)
{
	if (d.contains(key))
	{
		object o = d[key];

		try
		{
			*value = o.cast<char>();
		}
		catch (const error_already_set &e)
		{
			cout << e.what() << endl;
		}
	}
};


//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ���������ֵ������ṹ������ֵ��
void getString(dict d, const char *key, char *value)
{
	if (d.contains(key))
	{
		object o = d[key];
		try
		{
			string s = o.cast<string>();
			const char *buf = s.c_str();

#ifdef _MSC_VER //WIN32
			strcpy_s(value, strlen(buf) + 1, buf);
#elif __GNUC__
			strncpy(value, buffer, strlen(buffer) + 1);
#endif
		}
		catch (const error_already_set &e)
		{
			cout << e.what() << endl;
		}
	}
};

//��GBK������ַ���ת��ΪUTF8
string toUtf(string strGb2312)
{
	std::vector<wchar_t> buff(strGb2312.size());
#ifdef _MSC_VER
	std::locale loc("zh-CN");
#else
	std::locale loc("zh_CN.GB18030");
#endif
	wchar_t* pwszNext = nullptr;
	const char* pszNext = nullptr;
	mbstate_t state = {};
	int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
		(loc).in(state,
			strGb2312.data(), strGb2312.data() + strGb2312.size(), pszNext,
			buff.data(), buff.data() + buff.size(), pwszNext);

	if (std::codecvt_base::ok == res)
	{
		std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
		return cutf8.to_bytes(std::wstring(buff.data(), pwszNext));
	}

	return "";
}


