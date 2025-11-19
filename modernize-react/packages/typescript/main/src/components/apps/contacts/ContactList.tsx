// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext, useEffect, useState } from 'react';
import { List } from '@mui/material';
import { ContactContext } from 'src/context/ConatactContext/index'
import Scrollbar from 'src/components/custom-scroll/Scrollbar';
import ContactListItem from './ContactListItem';
import type { ContactType } from 'src/types/apps/contact';

type Props = {
  showrightSidebar: () => void;
};

const ContactList = ({ showrightSidebar }: Props) => {

  const {
    selectedDepartment,
    contacts,
    deleteContact,
    starredContacts,
    toggleStarred,
    setSelectedContact,
    selectedContact,
    searchTerm,

  }: any = useContext(ContactContext);



  // Filter contacts based on selected department and search query
  const filterContacts = (
    contacts: ContactType[],
    selectedDepartment: string,
    search: string
  ): ContactType[] => {
    let filteredContacts = [...contacts];
    if (selectedDepartment !== "All") {
      if (selectedDepartment === "Frequent") {
        filteredContacts = filteredContacts.filter(
          (contact) => contact.frequentlycontacted
        );
      } else if (selectedDepartment === "Starred") {
        filteredContacts = filteredContacts.filter((contact) =>
          starredContacts.includes(contact.id)
        );
      } else {
        filteredContacts = filteredContacts.filter(
          (contact) => contact.department === selectedDepartment
        );
      }
    }

    if (searchTerm.trim() !== "") {
      const searchTermLower = search.toLowerCase();
      filteredContacts = filteredContacts.filter(
        (contact) =>
          contact.firstname.toLowerCase().includes(searchTermLower) ||
          contact.lastname.toLowerCase().includes(searchTermLower)
      );
    }

    return filteredContacts;
  };

  // Get filtered contacts based on selected department and search query
  const filteredContacts = filterContacts(
    contacts,
    selectedDepartment,
    searchTerm
  );

  const handleContactClick = (contact: ContactType | any) => {
    setSelectedContact(contact);

  };


  const handleStarredClick = (contactId: number | string) => {
    toggleStarred(contactId);
  };


  return (
    <List>
      <Scrollbar sx={{ height: { lg: 'calc(100vh - 100px)', md: '100vh' }, maxHeight: '800px' }}>
        {filteredContacts.map((contact) => (
          <ContactListItem
            key={contact.id}
            active={contact.id === selectedContact?.id}
            {...contact}
            onContactClick={() => {
              handleContactClick(contact);
              showrightSidebar();
            }}
            onDeleteClick={() => deleteContact(contact.id)}
            onStarredClick={() => handleStarredClick(contact?.id)}
          />
        ))}
      </Scrollbar>
    </List>
  );
};

export default ContactList;