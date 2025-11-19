"use client"
import React, { createContext, useState, Dispatch, SetStateAction, useEffect } from 'react';

import useSWR from 'swr';
import { deleteFetcher, getFetcher } from 'src/api/globalFetcher';


const initialEmailContext = {
    emails: [],
    selectedEmail: null,
    filter: 'inbox',
    searchQuery: '',
    loading: true,
    error: null,
    setSelectedEmail: () => { },
    deleteEmail: () => { },
    toggleStar: () => { },
    toggleImportant: () => { },
    setFilter: () => { },
    setSearchQuery: () => { },
};

export const EmailContext = createContext(initialEmailContext);

export const EmailContextProvider = ({ children }) => {
    const [emails, setEmails] = useState([]);
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [filter, setFilter] = useState('inbox');
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { data: emailData, isLoading: isEmailLoading, error: emailError, mutate } = useSWR("/api/data/email/EmailData", getFetcher);

    useEffect(() => {
        if (emailData) {
            setEmails(emailData.data);
            if (emails?.length == 0) {
                setSelectedEmail(emailData.data[0]);
            }
            setLoading(isEmailLoading);
        } else if (emailError) {
            setError(emailError);
            setLoading(isEmailLoading);
        } else {
            setLoading(isEmailLoading);
        }
    }, [emailData, emailError, isEmailLoading, emails?.length]);

    const deleteEmail = async (emailId) => {
        try {

            await mutate(deleteFetcher('/api/data/email/delete', { emailId }));

            if (selectedEmail && selectedEmail.id === emailId) {
                setSelectedEmail(null);
            }

        } catch (error) {
            console.error('Error deleting email:', error);
        }
    };

    const toggleStar = (emailId) => {
        setEmails(prevEmails =>
            prevEmails.map(email =>
                email.id === emailId ? { ...email, starred: !email.starred } : email
            )
        );

        if (selectedEmail?.id === emailId) {
            setSelectedEmail((prevEmail) => ({
                ...(prevEmail),
                starred: !(prevEmail).starred
            }));
        }
    };

    const toggleImportant = (emailId) => {
        setEmails(prevEmails =>
            prevEmails.map(email =>
                email.id === emailId ? { ...email, important: !email.important } : email
            )
        );

        if (selectedEmail?.id === emailId) {
            setSelectedEmail((prevEmail) => ({
                ...(prevEmail),
                important: !(prevEmail).important
            }));
        }
    };

    return (
        <EmailContext.Provider value={{ emails, selectedEmail, setSelectedEmail, deleteEmail, toggleStar, toggleImportant, setFilter, filter, error, loading, searchQuery, setSearchQuery }}>
            {children}
        </EmailContext.Provider>
    );
};