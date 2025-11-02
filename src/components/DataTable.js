import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { DataTable as PaperDataTable, Text } from 'react-native-paper';

export const DataTable = ({ data, columns, title }) => {
  if (!data || data.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>暂无数据</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {title && <Text style={styles.title}>{title}</Text>}
      <ScrollView horizontal>
        <View>
          <PaperDataTable>
            <PaperDataTable.Header>
              {columns.map((col, index) => (
                <PaperDataTable.Title
                  key={index}
                  style={[styles.cell, { width: col.width || 120 }]}
                >
                  {col.label}
                </PaperDataTable.Title>
              ))}
            </PaperDataTable.Header>

            <ScrollView style={styles.tableBody}>
              {data.map((row, rowIndex) => (
                <PaperDataTable.Row key={rowIndex}>
                  {columns.map((col, colIndex) => (
                    <PaperDataTable.Cell
                      key={colIndex}
                      style={[styles.cell, { width: col.width || 120 }]}
                    >
                      <Text numberOfLines={col.multiline ? undefined : 2}>
                        {row[col.key] !== undefined && row[col.key] !== null
                          ? String(row[col.key])
                          : '-'}
                      </Text>
                    </PaperDataTable.Cell>
                  ))}
                </PaperDataTable.Row>
              ))}
            </ScrollView>
          </PaperDataTable>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  tableBody: {
    maxHeight: 400,
  },
  cell: {
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});
