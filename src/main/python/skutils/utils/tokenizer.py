#-*- encoding: utf8 -*-
__author__ = 'flappy'

# import jieba
# import jieba.posseg as pseg


isEn = lambda x: 'a' <= x <= 'z' or 'A' <= x <= 'Z'
isNum = lambda x: '0' <= x <= '9'
isAlphaNum = lambda x: isEn(x) or isNum(x)

class Tokenize:

    # !!! with caution, all segmented words in unicode
    # # 默认删除了空格

    # @staticmethod
    # def jieba(text, user_words=None):
    #     if user_words:
    #         for _ in user_words:
    #             jieba.add_word(_)
    #     return [w for w, t in pseg.cut(text) if not unicode.isspace(w)] # 默认删除了空格

    @staticmethod
    def char(text):
        # utext = text.decode('utf8')
        utext = text
        res = []
        en = ''
        for w in utext:
            # print 'curr:', w
            if unicode.isspace(w): # # 默认删除了空格
                continue
            if isAlphaNum(w):
                # print 'alphanum:', w
                en += w
            else:
                if en:
                    res.append(en)
                    en = ''
                res.append(w)
        if en:
            res.append(en)
        return res



if __name__ == '__main__':
    test = '你'.decode('utf8')
    print 'a' <= test <= 'z'

    sent = "我今天上山大老虎23333, 在bilibili上直播3小时".decode('utf8')

    for w in Tokenize.char(sent):
        print w

