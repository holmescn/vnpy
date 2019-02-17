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
void getInt(const dict &d, const char *key, int *value)
{
    if (d.contains(key))		//����ֵ����Ƿ���ڸü�ֵ
    {
        object o = d[key];		//��ȡ�ü�ֵ
        *value = o.cast<int>();
    }
};


//���ֵ��л�ȡĳ����ֵ��Ӧ�ĸ�����������ֵ������ṹ������ֵ��
void getDouble(const dict &d, const char *key, double *value)
{
    if (d.contains(key))
    {
        object o = d[key];
        *value = o.cast<double>();
    }
};


//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ�������ֵ������ṹ������ֵ��
void getChar(const dict &d, const char *key, char *value)
{
    if (d.contains(key))
    {
        object o = d[key];
        *value = o.cast<char>();
    }
};


template <size_t size>
using string_literal = char[size];

//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ���������ֵ������ṹ������ֵ��
template <size_t size>
void getString(const pybind11::dict &d, const char *key, string_literal<size> &value)
{
    if (d.contains(key))
    {
        object o = d[key];
        std::string s = o.cast<std::string>();
        const char *buf = s.c_str();
        strcpy(value, buf);
    }
};

//��GBK������ַ���ת��ΪUTF8
inline std::string toUtf(const std::string &gb2312)
{
#ifdef _MSC_VER
    const static std::locale loc("zh-CN");
#else
    const static std::locale loc("zh_CN.GB18030");
#endif

    std::vector<wchar_t> wstr(gb2312.size());
    wchar_t* wstrEnd = nullptr;
    const char* gbEnd = nullptr;
    std::mbstate_t state = {};
    int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
        (loc).in(state,
            gb2312.data(), gb2312.data() + gb2312.size(), gbEnd,
            wstr.data(), wstr.data() + wstr.size(), wstrEnd);

    if (std::codecvt_base::ok == res)
    {
        std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
        return cutf8.to_bytes(std::wstring(wstr.data(), wstrEnd));
    }

    return std::string();
}
