import { createContext, useState, useEffect } from 'react';

import React from "react";

import useSWR from 'swr';
import { deleteFetcher, getFetcher, postFetcher, putFetcher } from 'src/api/globalFetcher';




export const ContactContext = createContext(undefined);
export const ContactContextProvider = ({ children }) => {
  const [contacts, setContacts] = useState([]);
  const [starredContacts, setStarredContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [openModal, setOpenModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  // Fetch contacts data from the API on component mount
  const { data: contactsData, isLoading: isContactsLoading, error: contactsError, mutate } = useSWR('/api/data/contacts/contactsData', getFetcher);

  useEffect(() => {

    if (contactsData) {
      const allContacts = contactsData.data;
      setContacts(allContacts);
      if (contacts.length === 0) {
        const initialStarredContacts = allContacts.filter((contact) => contact.starred).map((contact) => contact.id);
        setStarredContacts(initialStarredContacts);
        setSelectedContact(allContacts[0]);
      }

    } else if (contactsError) {
      setLoading(isContactsLoading);
      setError(contactsError);
    } else {
      setLoading(isContactsLoading);
    }

  }, [contactsData, contactsError, isContactsLoading, contacts.length]);

  const updateSearchTerm = (term) => {
    setSearchTerm(term);
  };

  // Function to add Contact
  const addContact = async (newContact) => {
    try {
      await mutate(postFetcher("/api/data/contacts/addContact", newContact));
    } catch (error) {
      console.log("Failed to add contact", error)
    }
  };


  // Function to delete a contact
  const deleteContact = async (contactId) => {
    try {
      await mutate(deleteFetcher("/api/data/contacts/deleteContact", { data: { contactId } }));

      if (selectedContact && selectedContact.id === contactId) {
        setSelectedContact(null);
      }
    } catch (error) {
      console.error('Failed to delete contact:', error);
    }
  };


  // Function to update a contact
  const updateContact = async (updatedContact) => {
    try {
      await mutate(putFetcher("/api/data/contacts/updateContact", updatedContact));
      setSelectedContact(updatedContact);
    } catch (error) {
      console.error('Failed to update contact:', error);
    }
  };
  // Function to select a contact
  const selectContact = (contact) => {
    setSelectedContact(contact);
  };

  // Function to toggle the starred status of a contact
  const toggleStarred = (contactId) => {
    // Toggle the starredContacts array
    if (starredContacts.includes(contactId)) {
      setStarredContacts(prevStarred => prevStarred.filter(id => id !== contactId));
    } else {
      setStarredContacts(prevStarred => [...prevStarred, contactId]);
    }

    // Update the contacts list to reflect the new starred status
    setContacts(prevContacts => {
      const updatedContacts = prevContacts.map(contact =>
        contact.id === contactId
          ? { ...contact, starred: !contact.starred } // Toggle the starred status
          : contact
      );

      // If the selected contact is the one that was toggled, update the selectedContact state
      if (selectedContact?.id === contactId) {
        setSelectedContact(updatedContacts.find(contact => contact.id === contactId) || null);
      }

      return updatedContacts;
    });
  };

  // Value provided by the context provider
  const contextValue = {
    selectedDepartment,
    setSelectedDepartment,
    contacts,
    setContacts,
    starredContacts,
    setStarredContacts,
    selectedContact,
    setSelectedContact,
    addContact,
    deleteContact,
    updateContact,
    error,
    loading,
    selectContact,
    toggleStarred,
    searchTerm,
    updateSearchTerm,
    openModal, setOpenModal
  };

  return (
    <ContactContext.Provider value={contextValue}>
      {children}
    </ContactContext.Provider>
  );
};
