---
title: "Using pgAssistant with Infomaniak’s AI Cloud"
date: 2025-07-27
tags: ["AI", "Privacy", "Infomaniak"]
draft: false
---

# Privacy
 
Data privacy is no longer a luxury — it’s a necessity.

Today, we’ll show you how to use pgAssistant with [Infomaniak Cloud](https://www.infomaniak.com/fr/hebergement/ai-tools) — Infomaniak's privacy-focused, sovereign cloud solution based in Switzerland🇨.

---

## Why Data Sovereignty Matters

When using AI tools in the cloud, where your data is processed and stored has a major impact:

- **Legal compliance (e.g. GDPR)**
- **Data residency requirements**
- **Protection from mass surveillance**

Infomaniak’s Swiss Cloud is one of the few solutions that:
- Is fully hosted in **Switzerland**
- Operates under strict **Swiss privacy laws**
- Is ISO 27001 / GDPR compliant
- Powered by **renewable energy**

Perfect match for privacy-conscious developers and European companies.

---

## How to use my Infomaniak account with pgAssistant

I recommend to use the **llama3** model with pgAssistant, which gives good results.

The Environment variable LOCAL_LLM_URI must contains your **product ID** like this : https://api.infomaniak.com/1/ai/<productid>/openai
    
The Environment variable OPENAI_API_KEY is the value of your **token API**.
    
    
## docker-compose.yml file with Infomaniak account
```  
services:
  pgassistant:
    image: nexsoltech/pgassistant:latest
    restart: always
    environment:
      - OPENAI_API_KEY=fGIDaOIfn-xxxxx
      - OPENAI_API_MODEL=llama3
      - LOCAL_LLM_URI=https://api.infomaniak.com/1/ai/108043/openai
      - SECRET_KEY=bertrand
    ports:
      - "8080:5005"
    volumes:
      - ./myqueries.json:/home/pgassistant/myqueries.json
```

---

## Sample result with table definition helper

Lets analyze this DDL with llama3 hosted by Infomaniak :

![Analyze](/pgassistant-blog/images/infomaniak_tabledef.webp)

and here is the result :

![Result](/pgassistant-blog/images/infomaniak_tabledef.webp)

---

## Conclusion

If you don’t have the resources to set up an on-premise infrastructure capable of running open-source LLMs, but data privacy still matters to you, then Infomaniak’s sovereign cloud is definitely worth considering.

I’ve been using it personally for several months and I’m genuinely impressed. For me, it checks all the right boxes:

✅ Strong privacy guarantees

✅ Affordable pricing (my pricing this month for Input tokens : 1082936, Output tokens : 123411 = 1.82 EUR. With OpenAI, estimated price : 15 EUR)

✅ Solid performance

Just to be clear: I have no commercial relationship with Infomaniak — this is simply a personal recommendation based on real usage.

