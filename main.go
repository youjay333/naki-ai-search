package main

import (
	"context"
	"github.com/cloudwego/eino-ext/components/model/ark"
	"github.com/cloudwego/eino/schema"
	"github.com/joho/godotenv"
	"log"
	"os"
	"time"
)

func main() {
	err := godotenv.Load() // 加载环境变量
	if err != nil {
		log.Fatal("Error loading .env file") // 处理加载错误
	}
	ctx := context.Background()
	timeout := 60 * time.Second

	//新建模型
	model, err := ark.NewChatModel(ctx, &ark.ChatModelConfig{
		APIKey:  os.Getenv("ARK_API_KEY"),
		Model:   os.Getenv("MODEL"),
		Timeout: &timeout,
	})
	if err != nil {
		panic(err)
	}
	// 准备消息
	messages := []*schema.Message{
		schema.SystemMessage("你是一个eino框架的开发助手"),
		schema.UserMessage("eino是个什么东西？"),
	}
	// 生成回复
	response, err := model.Generate(ctx, messages)
	if err != nil {
		panic(err)
	}
	// 处理回复
	println(response.Content)
	// 获取 Token 使用情况
	if usage := response.ResponseMeta.Usage; usage != nil {
		println("提示 Tokens:", usage.PromptTokens)
		println("生成 Tokens:", usage.CompletionTokens)
		println("总 Tokens:", usage.TotalTokens)
	}

}
