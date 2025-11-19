'use client'
import { createContext, useState, useEffect } from 'react';
import React from "react";
import useSWR from 'swr';

import { getFetcher, postFetcher } from 'src/api/globalFetcher';


// Create the context
export const ChatContext = createContext({
    chatData: [],
    chatContent: [],
    chatSearch: '',
    selectedChat: null,
    loading: true,
    error: '',
    activeChatId: null,
    setChatContent: () => { },
    setChatSearch: () => { },
    setSelectedChat: () => { },
    setActiveChatId: () => { },
    sendMessage: () => { },
    setLoading: () => { },
    setError: () => { },
});

// Create the provider component
export const ChatProvider = ({ children }) => {
    const [chatData, setChatData] = useState([]);
    const [chatContent, setChatContent] = useState([]);
    const [chatSearch, setChatSearch] = useState('');
    const [selectedChat, setSelectedChat] = useState(null);
    const [activeChatId, setActiveChatId] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const { data: ChatsData, isLoading: isChatsLoading, error: Chatserror, mutate } = useSWR('/api/data/chat/ChatData', getFetcher);

    // Fetch chat data from the API
    useEffect(() => {
        if (ChatsData) {
            setLoading(isChatsLoading);
            const chatsData = ChatsData.data;
            if (chatData.length === 0) {
                let specificChat = chatsData[0];
                setSelectedChat(specificChat);
            }
            setChatData(chatsData);
        } else if (Chatserror) {
            setError(Chatserror)
            setLoading(isChatsLoading);
            console.log("Failed to fetch the data")
        }
        else {
            setLoading(isChatsLoading);
        }
    }, [ChatsData, Chatserror, isChatsLoading, chatData.length]);

    // Function to send a message to a chat identified by `chatId` using an API call.
    const sendMessage = async (chatId, message) => {
        try {
            let { data } = await mutate(postFetcher('/api/sendMessage', { chatId, message }));
            let chat = data.find((chat) => chat.id === chatId)
            setSelectedChat(chat);
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    const value = {
        chatData,
        chatContent,
        chatSearch,
        selectedChat,
        loading,
        error,
        activeChatId,
        setChatContent,
        setChatSearch,
        setSelectedChat,
        setActiveChatId,
        sendMessage,
        setError,
        setLoading,
    };
    return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};


